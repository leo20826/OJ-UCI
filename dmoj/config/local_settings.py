#####################################
########## Django settings ##########
#####################################
# See <https://docs.djangoproject.com/en/5.0/ref/settings/>

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', '')
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', '0') == '1'
HOST = os.environ.get('HOST', 'localhost')

ALLOWED_HOSTS = [HOST]

# Optional apps that DMOJ can make use of.
INSTALLED_APPS += ()

# Caching. You can use memcached or redis instead.
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_CACHING_URL', 'redis://redis:6379/0'),
    },
}

# Your database credentials. Only MySQL is supported by DMOJ.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('MYSQL_DATABASE', 'dmoj'),
        'USER': os.environ.get('MYSQL_USER', 'dmoj'),
        'PASSWORD': os.environ.get('MYSQL_PASSWORD', ''),
        'HOST': os.environ.get('MYSQL_HOST', 'db'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'sql_mode': 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION',
        },
    },
}

# Internationalization.
LANGUAGE_CODE = 'en'
DEFAULT_USER_TIME_ZONE = 'America/Havana'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# django-compressor settings
COMPRESS_OUTPUT_DIR = 'cache'
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.CSSMinFilter',
]
COMPRESS_JS_FILTERS = ['compressor.filters.jsmin.JSMinFilter']
COMPRESS_STORAGE = 'compressor.storage.GzipCompressorFileStorage'
STATICFILES_FINDERS += ('compressor.finders.CompressorFinder',)

# Email configuration
ADMINS = ()
SERVER_EMAIL = 'OJ: Online Judge <oj@email.com>'

# Static files configuration
STATIC_ROOT = '/assets/static/'
STATIC_URL = '/static/'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
DMOJ_RESOURCES = '/assets/resources/'

# DMOJ site display settings
SITE_NAME = 'OJ'
SITE_FULL_URL = os.environ.get('SITE_FULL_URL', 'http://localhost/')
SITE_LONG_NAME = 'OJ: Online Judge'
SITE_ADMIN_EMAIL = 'adminc@email.com'
TERMS_OF_SERVICE_URL = None

# Media files settings
MEDIA_ROOT = '/media/'
MEDIA_URL = os.environ.get('MEDIA_URL', 'http://localhost/')

# Problem data settings
DMOJ_PROBLEM_DATA_ROOT = '/problems/'

# Bridge controls
BRIDGED_JUDGE_ADDRESS = [(os.environ.get('BRIDGED_HOST', 'bridged'), 9999)]
BRIDGED_DJANGO_ADDRESS = [(os.environ.get('BRIDGED_HOST', 'bridged'), 9998)]

# DMOJ features
ENABLE_FTS = False
BAD_MAIL_PROVIDERS = set()

# Event server
EVENT_DAEMON_USE = True
EVENT_DAEMON_POST = os.environ.get('EVENT_DAEMON_POST', 'ws://wsevent:15101/')
EVENT_DAEMON_GET = f'ws://{HOST}/event/'
EVENT_DAEMON_GET_SSL = f'wss://{HOST}/event/'
EVENT_DAEMON_POLL = '/channels/'

# Celery
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/1')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379/1')

# CDN control
ACE_URL = '//cdnjs.cloudflare.com/ajax/libs/ace/1.2.3/'
JQUERY_JS = '//cdnjs.cloudflare.com/ajax/libs/jquery/2.2.4/jquery.min.js'
SELECT2_JS_URL = '//cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/js/select2.min.js'
SELECT2_CSS_URL = '//cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/css/select2.min.css'

TIMEZONE_MAP = 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Blue_Marble_2002.png/1024px-Blue_Marble_2002.png'

# Custom configuration
FILE_UPLOAD_PERMISSIONS = 0o644
VNOJ_CP_TICKET = 5

REGISTRATION_OPEN = True
DMOJ_RATING_COLORS = True
X_FRAME_OPTIONS = 'DENY'