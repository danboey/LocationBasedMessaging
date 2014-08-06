"""
Django settings for lbm project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '8uxrtc942wi=ur!*5p9ysj%-7gf9z!xz^c8vpb@u3uz9_xi)ot'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'lbm_mong',
    'tastypie',
    'tastypie_mongoengine',
    'social.apps.django_app.me',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'lbm.urls'

WSGI_APPLICATION = 'lbm.wsgi.application'


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

SOCIAL_AUTH_STORAGE = 'social.apps.django_app.me.models.DjangoStorage'

AUTHENTICATION_BACKENDS = (
   'social.backends.facebook.FacebookOAuth2',
   'django.contrib.auth.backends.ModelBackend',
   'mongoengine.django.auth.MongoEngineBackend',
   'lbm_mong.back.PersonAuthBackend',
)

SOCIAL_AUTH_USER_MODEL = 'lbm_mong.models.Person'

SESSION_ENGINE = 'mongoengine.django.sessions'

MONGO_DATABASE_NAME = 'lbm_mongo_key'

from mongoengine import connect
connect(MONGO_DATABASE_NAME)

