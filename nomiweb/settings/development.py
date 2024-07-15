from .base import *
from decouple import config

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'En_dev_no_importa'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

SETTINGS_ENV = 'development'


# Carga las variables de entorno desde el archivo .env
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nomiweb.settings.development')



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'userlectaen',
        'USER': config('DB_USER_DEV'),
        'PASSWORD': config('DB_PASSWORD_DEV'),
        'HOST': config('DB_HOST_DEV'),
        'PORT': config('DB_PORT_DEV'),
    },
    'lectaen': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'lectaen',
        'USER': config('DB_USER_DEV'),
        'PASSWORD': config('DB_PASSWORD_DEV'),
        'HOST': config('DB_HOST_DEV'),
        'PORT': config('DB_PORT_DEV'),
    },
    'nwp_2': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nwp_lentes',
        'USER': config('DB_USER_DEV'),
        'PASSWORD': config('DB_PASSWORD_DEV'),
        'HOST': config('DB_HOST_DEV'),
        'PORT': config('DB_PORT_DEV'),
    }
}



STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, '..', 'static')
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')