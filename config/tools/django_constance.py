# pip install django-constance[database]
# Añadir a INSTALLED_APPS en base.py:
#   'constance',
#   'constance.backends.database',

CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

CONSTANCE_CONFIG = {
    # Tipo de cambio del día (HU08)
    'TIPO_CAMBIO_USD': (3.75, 'Tipo de cambio USD → PEN del día', float),
    # Porcentaje de adelanto por defecto (HU11)
    'PORCENTAJE_ADELANTO_DEFAULT': (50, 'Porcentaje de adelanto por defecto en proformas (%)', int),
    # Nombre de la empresa emisora
    'EMPRESA_NOMBRE': ('Gibit Tecnología S.A.C.', 'Nombre de la empresa para documentos', str),
    'EMPRESA_RUC': ('', 'RUC de la empresa emisora', str),
    'EMPRESA_DIRECCION': ('', 'Dirección fiscal de la empresa emisora', str),
}

CONSTANCE_CONFIG_FIELDSETS = {
    'Finanzas': ('TIPO_CAMBIO_USD', 'PORCENTAJE_ADELANTO_DEFAULT'),
    'Datos de la empresa': ('EMPRESA_NOMBRE', 'EMPRESA_RUC', 'EMPRESA_DIRECCION'),
}
