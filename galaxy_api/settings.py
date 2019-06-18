"""
Django settings for galaxy_api project.

Generated by 'django-admin startproject' using Django 2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '-la_p$f%^0b1n)#00t6(rk#un4c4-^zqlmkeeqibl5l9t6)pui'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.messages',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.staticfiles',
    'rest_framework',
    'drf_yasg',
    'api'
]

STATIC_URL = '/static/'
SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'galaxy_api.urls'

WSGI_APPLICATION = 'galaxy_api.wsgi.application'

TEMPLATE_LOADERS = [
    'django.template.loaders.app_directories.Loader'
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

API_KEY_HEADER_NAME = 'X-Api-Key'

API_KEY = None  # configure

SWAGGER_SETTINGS = {
    'DEFAULT_INFO': 'api.urls.api_info',
    'USE_SESSION_AUTH': False,
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            "type": "apiKey",
            "name": API_KEY_HEADER_NAME,
            "in": "header"
        }
    }
}

# Queries directory settings

QUERIES_DIR = os.path.join(BASE_DIR, 'galaxy-descriptions')

# Pagination settings

PAGE_QUERY_PARAM = 'page'
PAGE_SIZE_QUERY_PARAM = 'pagesize'
DEFAULT_PAGE_SIZE = 20

LOG_ROOT = os.path.join(BASE_DIR, "log")

LOG_HANDLERS = ['console', 'logfile', ]

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

DEBUG_TRUE_LOG_LEVEL = 'INFO'

DEBUG_FALSE_LOG_LEVEL = 'WARNING'

from galaxy_api.local_settings import *

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
    'galaxy_db': {
        'ENGINE': 'sql_server.pyodbc',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,

        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    }
}

if not os.path.exists(LOG_ROOT):
    os.makedirs(LOG_ROOT)

__debug_log_level = DEBUG_TRUE_LOG_LEVEL if DEBUG else DEBUG_FALSE_LOG_LEVEL

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
    },
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'logfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_ROOT + '/logfile.log',
            'maxBytes': 5 * 1024 * 1024,
            'backupCount': 1000,
            'encoding': 'utf8',
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'] + list(LOG_HANDLERS),
            'level': 'ERROR',
            'propagate': True,
        },
        'api': {
            'handlers': LOG_HANDLERS,
            'level': __debug_log_level,
            'formatter': 'verbose'
        },
    }
}
