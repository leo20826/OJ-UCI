# throttle_mail.py
import traceback

from django.conf import settings
from django.core.cache import cache
from django.utils.log import AdminEmailHandler

DEFAULT_THROTTLE = (10, 60)


def new_email():
    """
    Incrementa y devuelve el contador de emails en el periodo de throttling.
    Implementación tolerante a distintos backends de cache.
    """
    key = 'error_email_throttle'
    throttle_cfg = getattr(settings, 'DMOJ_EMAIL_THROTTLING', DEFAULT_THROTTLE)
    timeout = throttle_cfg[1]

    # Intenta uso atómico con incr (backends como django-redis/memcached)
    try:
        if not cache.get(key):
            cache.add(key, 0, timeout)
        return cache.incr(key)
    except (ValueError, NotImplementedError, AttributeError):
        # Fallback para backends sin incr
        try:
            current = cache.get(key)
            if current is None:
                created = cache.add(key, 1, timeout)
                if created:
                    return 1
                current = cache.get(key, 0)
            new = int(current) + 1
            cache.set(key, new, timeout)
            return new
        except Exception:
            # Si la cache falla por completo, devolvemos 1 por seguridad
            return 1


class ThrottledEmailHandler(AdminEmailHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        throttle_cfg = getattr(settings, 'DMOJ_EMAIL_THROTTLING', DEFAULT_THROTTLE)
        self.throttle = throttle_cfg[0]

    def emit(self, record):
        try:
            count = new_email()
        except Exception:
            # No queremos que un fallo de la cache rompa el logging principal.
            traceback.print_exc()
            count = None
        else:
            if count is not None and count >= self.throttle:
                return

        # Intentar enviar el mail usando el comportamiento base; si falla,
        # capturarlo y usar handleError para que logging no escale excepción.
        try:
            super().emit(record)
        except Exception:
            # Registrar internamente y evitar que el logger falle
            self.handleError(record)
