# pip install django-easy-audit
# Añadir a INSTALLED_APPS en base.py:
#   'easyaudit',
# Añadir a MIDDLEWARE en base.py (antes del cierre):
#   'easyaudit.middleware.easyaudit.EasyAuditMiddleware',

# Modelos que se auditarán (HU23 - control de acceso y auditoría)
DJANGO_EASY_AUDIT_REGISTERED_MODELS = [
    'apps.clientes.Empresa',
    'apps.clientes.Sede',
    'apps.clientes.Contacto',
    # Fase 3+:
    # 'apps.proformas.Proforma',
    # 'apps.proyectos.Proyecto',
]

# No auditar modelos de sesión ni admin logs (mucho ruido)
DJANGO_EASY_AUDIT_UNREGISTERED_CLASSES_EXTRA = [
    'django.contrib.sessions.models.Session',
    'django.contrib.admin.models.LogEntry',
]

DJANGO_EASY_AUDIT_WATCH_AUTH_EVENTS = True
DJANGO_EASY_AUDIT_WATCH_REQUEST_EVENTS = False
