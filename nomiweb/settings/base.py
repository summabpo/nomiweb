import os
from dotenv import load_dotenv
# from django.urls import reverse_lazy

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Cargar las variables de entorno desde el archivo .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(BASE_DIR), '.env'))



SETTINGS_ENV = 'base'

# Application definition

BASE_APPS = [
    # Django REST Framework
    'rest_framework',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'storages',
    'apps.common',
]

LOCAL_APPS = [
    # Generated applications
    
    'apps.login', 
    'apps.employees',     # Employees application
    #'apps.companies',     # Companies application
    #'apps.administrator',
    # 'apps.payroll',       # Payroll application
    # 'apps.api_database',  # API database applicatio#n
]
THIRD_APPS = [
    # Crispy Forms
    'crispy_forms',
    "crispy_bootstrap5",
    # Importar excel
    'import_export',
    ## Debug toolbar
    'debug_toolbar',
]

INSTALLED_APPS = BASE_APPS + LOCAL_APPS + THIRD_APPS

INTERNAL_IPS = [
    '127.0.0.1',
]


CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'

CRISPY_TEMPLATE_PACK = 'bootstrap5'

BASE_MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

LOCAL_MIDDLEWARE = [
    
]

THIRD_MIDDLEWARE = [

]

MIDDLEWARE = BASE_MIDDLEWARE + LOCAL_MIDDLEWARE + THIRD_MIDDLEWARE


ROOT_URLCONF = 'nomiweb.urls'




TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, '..', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'nomiweb.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases




AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Esto es opcional, pero es una buena práctica
]

SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # O el backend que estés usando
SESSION_COOKIE_AGE = 1209600  # Duración de la sesión en segundos (2 semanas)
SESSION_SAVE_EVERY_REQUEST = True  # Guardar la sesión en cada solicitud
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # No expirar la sesión al cerrar el navegador




# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# SMTP email server config

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = os.environ.get('EMAIL_PORT')
EMAIL_USE_TLS = False
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_USE_SSL = True
EMAIL_TIMEOUT = None
EMAIL_SSL_KEYFILE = None
EMAIL_SSL_CERTFILE = None
EMAIL_SSL_CAFILE = None
EMAIL_SSL_CERT_SUBJ = None
EMAIL_SSL_CERT_PASSWD = None
EMAIL_SSL_CIPHER = None
EMAIL_USE_LOCALTIME = False
EMAIL_FILE_PATH = None
EMAIL_FROM = None
EMAIL_SUBJECT_PREFIX = '[Django] '

# settings.py

LOGIN_URL = '/'


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'es-co'

TIME_ZONE = 'America/Bogota'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/'




AUTH_USER_MODEL = 'common.User'