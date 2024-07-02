from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY =  os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS').split(',')

SETTINGS_ENV = 'production'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'userlectaen',
        'USER':  os.getenv('DB_USER_PROD'),
        'PASSWORD':  os.getenv('DB_PASSWORD_PROD'),
        'HOST':  os.getenv('DB_HOST_PROD'),
        'PORT':  os.getenv('DB_PORT_PROD'),
    },

    'lectaen': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'lectaen',
        'USER':  os.getenv('DB_USER_PROD'),
        'PASSWORD':  os.getenv('DB_PASSWORD_PROD'),
        'HOST':  os.getenv('DB_HOST_PROD'),
        'PORT':  os.getenv('DB_PORT_PROD'),
    } ,
    'nwp_2': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nwp_lentes',
        'USER':  os.getenv('DB_USER_PROD'),
        'PASSWORD':  os.getenv('DB_PASSWORD_PROD'),
        'HOST':  os.getenv('DB_HOST_PROD'),
        'PORT':  os.getenv('DB_PORT_PROD'),
    }
}