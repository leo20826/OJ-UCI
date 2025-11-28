"""
Django settings for dmoj project (actualizado para Django 4.2 LTS).

Notas:
- Migrado para ser compatible con Django 4.2 LTS.
- Cambios principales: actualizado de 5.2 a 4.2 LTS.
"""

from pathlib import Path
import datetime
import os

from django.utils.translation import gettext_lazy as _
from django_jinja.builtins import DEFAULT_EXTENSIONS
from jinja2 import select_autoescape

# Base dir (Pathlib)
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/  # CAMBIADO: 5.2 → 4.2

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '5*9f5q57mqmlz2#f$x1h76&jxy#yortjl1v+l*6hd18$d*yx#0'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# ... (TODO EL RESTO DEL CÓDIGO SE MANTIENE IGUAL HASTA LA SECCIÓN DE INTERNATIONALIZATION) ...

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/  # CAMBIADO: 5.2 → 4.2

# Whatever you do, this better be one of the entries in `LANGUAGES`.
LANGUAGE_CODE = 'en'
TIME_ZONE = 'UTC'
DEFAULT_USER_TIME_ZONE = 'America/Toronto'
USE_I18N = True
USE_TZ = True

# ... (TODO EL RESTO DEL CÓDIGO SE MANTIENE IGUAL HASTA LA SECCIÓN DE DATABASES) ...

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases  # CAMBIADO: 5.2 → 4.2

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
}

# ... (TODO EL RESTO DEL CÓDIGO SE MANTIENE IGUAL HASTA LA SECCIÓN DE STATIC FILES) ...

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/  # CAMBIADO: 5.2 → 4.2

DMOJ_RESOURCES = os.path.join(BASE_DIR, 'resources')
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'resources'),
]
STATIC_URL = '/static/'

# ... (TODO EL RESTO DEL CÓDIGO SE MANTIENE EXACTAMENTE IGUAL) ...