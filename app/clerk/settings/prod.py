# flake8: noqa
from . import *

DEBUG = False
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
ALLOWED_HOSTS = []

# Remove Django Debug Toolbar stuff
INSTALLED_APPS.remove('debug_toolbar')
MIDDLEWARE.remove('debug_toolbar.middleware.DebugToolbarMiddleware')
