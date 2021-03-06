"""
Django settings for lbm project.
"""


import os
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '8uxrtc942wi=ur!*5p9ysj%-7gf9z!xz^c8vpb@u3uz9_xi)ot'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*']


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
   'lbm_mong.back.MyUserAuthBackend',
)

SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'social.pipeline.user.get_username',
    'social.pipeline.user.create_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details',
    'lbm_mong.mypipeline.my_pipeline'
)

SOCIAL_AUTH_FACEBOOK_SCOPE = [
    'email',
    'user_friends',
]

SOCIAL_AUTH_USER_MODEL = 'lbm_mong.models.MyUser'

SOCIAL_AUTH_FACEBOOK_KEY = '302871443207881'

SOCIAL_AUTH_FACEBOOK_SECRET = 'b03f9ab5562b287fc7fe9aa704cbc2aa'

SESSION_ENGINE = 'mongoengine.django.sessions'


'''PUSH NOTIFICATION SETTINGS'''
'''PYAPNS_CONFIG = {
  'HOST': 'http://localhost:8077/',
  'TIMEOUT': 10,
  'INITIAL': [                      
    ('LocationBasedMessagingApp', '/path/to/cert/apscert.pem', 'sandbox'),
  ]
}'''

MONGO_DATABASE_NAME = 'lbm_mongo_key_again'

from mongoengine import connect
connect(MONGO_DATABASE_NAME)


