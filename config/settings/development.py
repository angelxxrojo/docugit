from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*', 'localhost', '127.0.0.1']

# En desarrollo, los correos se imprimen en consola
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# WhiteNoise en desarrollo no comprime para ser más rápido
STATICFILES_STORAGE = 'whitenoise.storage.StaticFilesStorage'
