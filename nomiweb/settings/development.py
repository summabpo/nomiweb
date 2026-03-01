from .base import *




#dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
#load_dotenv(dotenv_path)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY =  os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')


SETTINGS_ENV = 'development'

HOSTNAME = "https://dev.nomiweb.com.co/"


CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'https://localhost:8000',  # Si estás usando HTTPS
    'http://127.0.0.1:8000',
    'http://127.0.0.1:8081',
    'http://127.0.0.1:8000',
    'http://localhost:8081',
    'https://nomiweb.com.co',
    'https://app.nomiweb.com.co',
    'https://dev.nomiweb.com.co',
    'http://app.nomiweb.com.co',
    'http://dev.nomiweb.com.co',
    'http://nomiweb.com.co', 
    'http://payroll.nomiweb.co',
    'https://payroll.nomiweb.co',
    
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'migra_003',
        'USER':  os.getenv('DB_USER_DEV'),
        'PASSWORD':  os.getenv('DB_PASSWORD_DEV'),  
        'HOST':  os.getenv('DB_HOST_DEV'),
        'PORT':  os.getenv('DB_PORT_DEV'),
    },
    
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, '..', 'static')
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')