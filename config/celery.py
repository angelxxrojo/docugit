import os

from celery import Celery

# pip install celery redis
# Requiere un broker (Redis recomendado): pip install redis
# Iniciar worker: celery -A config worker -l info

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('gibit')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

# Configuración en base.py (descomentar cuando se instale):
# CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
# CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
# CELERY_ACCEPT_CONTENT = ['json']
# CELERY_TASK_SERIALIZER = 'json'
