# throttle_discord_webhook.py
import logging
import traceback
from copy import copy

from discord_webhook import DiscordWebhook
from django.conf import settings
from django.core.cache import cache
from django.views.debug import ExceptionReporter


def new_webhook():
    """
    Incrementa y devuelve el contador de webhooks en el periodo de throttling.
    Implementación tolerante a distintos backends de cache.
    """
    key = 'error_discord_webhook_throttle'
    timeout = getattr(settings, 'VNOJ_DISCORD_WEBHOOK_THROTTLING', (10, 60))[1]

    # Intenta usar incr directo (rápido y atómico en backends que lo soportan).
    try:
        # Asegurarnos de que la clave existe; si no existe, inicializarla a 0.
        if not cache.get(key):
            # cache.add devuelve True si creada, False si ya existía
            cache.add(key, 0, timeout)
        return cache.incr(key)
    except (ValueError, NotImplementedError, AttributeError):
        # Fallback no-atomico para caches que no implementan incr
        try:
            current = cache.get(key)
            if current is None:
                # intentamos crearla
                created = cache.add(key, 1, timeout)
                if created:
                    return 1
                # si no la creamos por race, leer de nuevo
                current = cache.get(key, 0)
            # sumar y guardar
            new = int(current) + 1
            cache.set(key, new, timeout)
            return new
        except Exception:
            # En caso de que la cache falle por completo, devolvemos 1 como comport.
            return 1


class ThrottledDiscordWebhookHandler(logging.Handler):
    """An exception log handler that sends log entries to a Discord webhook.

    If the request is passed as the first argument to the log record,
    request data will be provided in the message report.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Send at most (VNOJ_DISCORD_WEBHOOK_THROTTLING[0]) messages in
        # (VNOJ_DISCORD_WEBHOOK_THROTTLING[1]) seconds
        self.throttle = getattr(settings, 'VNOJ_DISCORD_WEBHOOK_THROTTLING', (10, 60))[0]

    def emit(self, record):
        # Adapt from `dmoj.throttle_mail.ThrottledEmailHandler`
        try:
            count = new_webhook()
        except Exception:
            # No queremos que un fallo de cache rompa el logging principal.
            traceback.print_exc()
            count = None
        else:
            # Si alcanzamos el límite, no hacemos nada
            if count is not None and count >= self.throttle:
                return

        # Adapt from `django.utils.log.AdminEmailHandler`
        request = None
        try:
            request = getattr(record, 'request', None)
            # Determine IP type (internal/external) defensivamente
            remote_addr = None
            if request is not None:
                remote_addr = request.META.get('REMOTE_ADDR')
            internal_ips = getattr(settings, 'INTERNAL_IPS', ())
            ip_type = 'internal' if (remote_addr and remote_addr in internal_ips) else 'EXTERNAL'
            subject = '%s (%s IP): %s' % (record.levelname, ip_type, record.getMessage())
        except Exception:
            subject = '%s: %s' % (record.levelname, record.getMessage())
            request = None

        # Make a copy of the record without exception info to avoid duplication
        no_exc_record = copy(record)
        no_exc_record.exc_info = None
        no_exc_record.exc_text = None

        if getattr(record, 'exc_info', None):
            exc_info = record.exc_info
        else:
            exc_info = (None, record.getMessage(), None)

        # ExceptionReporter signature: (request, exc_type, exc_value, tb)
        try:
            reporter = ExceptionReporter(request, exc_info[0], exc_info[1], exc_info[2])
            tb_text = reporter.get_traceback_text()
        except Exception:
            # Fallback simple traceback text
            tb_text = ''.join(traceback.format_exception(*exc_info)) if exc_info else record.getMessage()

        message = '%s\n\n%s' % (self.format(no_exc_record), tb_text)

        # Enviar webhook de forma robusta
        try:
            self.send_webhook(subject, message)
        except Exception:
            # Ensure logging does not raise in production
            self.handleError(record)

    def send_webhook(self, subject, message):
        webhook_url = settings.DISCORD_WEBHOOK.get('on_error', None)
        if not webhook_url:
            return

        try:
            webhook = DiscordWebhook(url=webhook_url, content=subject)
            # Discord limit ~8MB; usar 7MB como seguridad. encode -> bytes
            payload = message[:7 * 1024 * 1024].encode('utf-8', errors='replace')
            webhook.add_file(file=payload, filename='log.txt')
            webhook.execute()
        except Exception:
            # No queremos que errores de la API de Discord rompan nuestro logger
            raise
