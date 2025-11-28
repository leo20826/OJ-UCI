# dmoj/celery.py
import logging
import os
import socket

from celery import Celery
from celery.signals import task_failure

# Establecer settings module por defecto para entornos donde no esté configurado.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dmoj.settings')

app = Celery('dmoj')

# Cargar configuración desde Django settings con prefijo CELERY_*
app.config_from_object('django.conf:settings', namespace='CELERY')

# Si usas valores secretos diferentes (p. ej. inyectados por Docker/K8s), respetarlos.
from django.conf import settings  # noqa: E402 (django must be imported after env var set)
if hasattr(settings, 'CELERY_BROKER_URL_SECRET'):
    app.conf.broker_url = settings.CELERY_BROKER_URL_SECRET
if hasattr(settings, 'CELERY_RESULT_BACKEND_SECRET'):
    app.conf.result_backend = settings.CELERY_RESULT_BACKEND_SECRET

# Autodiscover tasks in installed apps (busca tasks.py)
app.autodiscover_tasks()

# Logger para reportar errores
logger = logging.getLogger('judge.celery')


@task_failure.connect()
def celery_failure_log(sender, task_id, exception, traceback, *args, **kwargs):
    logger.error(
        'Celery Task %s: %s on %s',
        sender.name,
        task_id,
        socket.gethostname(),  # noqa: G201
        exc_info=(type(exception), exception, traceback),
    )
