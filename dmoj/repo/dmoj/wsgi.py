import os

# Configuración del módulo de settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dmoj.settings')

# Compatibilidad MySQL: intenta MySQLdb, si no, usa PyMySQL
try:
    import MySQLdb  # noqa: F401, importado por efecto secundario
except ImportError:
    import pymysql
    pymysql.install_as_MySQLdb()

# Importa la aplicación WSGI de Django
from django.core.wsgi import get_wsgi_application  # Django debe ser importado aquí
application = get_wsgi_application()
