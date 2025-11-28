import os

import gevent.monkey  # Gevent must be imported and patched first
gevent.monkey.patch_all()

# Import PyMySQL installer for MySQL support (side effect)
import dmoj_install_pymysql  # noqa: F401

from django.core.wsgi import get_wsgi_application  # Django must be imported after monkey patch
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dmoj.settings')

# WSGI application
application = get_wsgi_application()
