"""
WSGI config for group project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os, sys    
sys.path.append(' /home/dan-ubuntu/Desktop/lbm_key_v3/lbm')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bookings.settings")
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
