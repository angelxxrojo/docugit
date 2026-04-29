from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.usuarios.urls')),
    path('clientes/', include('apps.clientes.urls')),
    path('location/', include('apps.location.urls')),
    path('catalogo/', include('apps.catalogo.urls')),
    path('proformas/', include('apps.proformas.urls')),
    path('proyectos/', include('apps.proyectos.urls')),
    path('docs/', include('apps.documentos.urls')),
    path('', include('apps.core.urls')),
    # path('portal/', include('apps.portal.urls')),
]

handler403 = 'django.views.defaults.permission_denied'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
