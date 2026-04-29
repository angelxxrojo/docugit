# pip install drf-spectacular
# Añadir a INSTALLED_APPS en base.py:
#   'drf_spectacular',
# Añadir a urls.py:
#   from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
#   path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
#   path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

SPECTACULAR_SETTINGS = {
    'TITLE': 'Gibit Tecnología — API',
    'DESCRIPTION': 'API del sistema de gestión documental y comercial de Gibit Tecnología.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'TAGS': [
        {'name': 'clientes', 'description': 'Gestión de empresas, sedes y contactos'},
        {'name': 'catalogo', 'description': 'Catálogo de servicios y condiciones'},
        {'name': 'proformas', 'description': 'Cotizaciones y versiones'},
        {'name': 'proyectos', 'description': 'Proyectos y contratos'},
        {'name': 'location', 'description': 'UBIGEO — departamentos, provincias, distritos'},
    ],
}
