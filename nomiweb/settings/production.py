from .base import *
from boto3.session import Session

import logging

# Cargar .env.production para settings de producción (sobrescribe variables de .env de base.py)
from dotenv import load_dotenv
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(dotenv_path=os.path.join(_project_root, '.env.production'), override=True)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY =  os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

SETTINGS_ENV = 'production'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME_PROD', 'nomiweb_payroll'),
        'USER':  os.getenv('DB_USER_PROD'),
        'PASSWORD':  os.getenv('DB_PASSWORD_PROD'),
        'HOST':  os.getenv('DB_HOST_PROD'),
        'PORT':  os.getenv('DB_PORT_PROD'),
    },
}

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, '..', 'static')
]

# Seguridad de cookies
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

HOSTNAME = os.getenv('HOSTNAME', 'https://payroll.nomiweb.co/')


CSRF_COOKIE_HTTPONLY = True

CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8081',
    'http://127.0.0.1:8000',
    'http://localhost:8081',
    'https://nomiweb.com.co',
    'https://app.nomiweb.com.co',
    'https://dev.nomiweb.com.co',
    'http://app.nomiweb.com.co',
    'http://dev.nomiweb.com.co',
    'http://nomiweb.com.co',
    'https://payroll.nomiweb.co',
    'http://payroll.nomiweb.co',
    'https://jes.nomiweb.com.co',
    'http://jes.nomiweb.com.co',
]


# Configuración de S3
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Almacén estático y de medios
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# URL estática y de medios
STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'

# Configuración de caché
AWS_QUERYSTRING_AUTH = False
AWS_S3_FILE_OVERWRITE = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
        },
    },
}