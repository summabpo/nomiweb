from .base import *




#dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
#load_dotenv(dotenv_path)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'En_dev_no_importa'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

SETTINGS_ENV = 'development'

HOSTNAME = "http://127.0.0.1:8000/"

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
    'http://nomiweb.com.co'
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nomiweb3',
        'USER':  os.getenv('DB_USER_DEV'),
        'PASSWORD':  os.getenv('DB_PASSWORD_DEV'),  
        'HOST':  os.getenv('DB_HOST_DEV'),
        'PORT':  os.getenv('DB_PORT_DEV'),
    },
    
}



STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, '..', 'static')
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')