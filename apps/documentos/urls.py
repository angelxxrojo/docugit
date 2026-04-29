from django.urls import path

from . import views

app_name = 'documentos'

urlpatterns = [
    # Plantillas
    path('plantillas/', views.PlantillaListView.as_view(), name='plantilla_list'),
    path('plantillas/nueva/', views.PlantillaCreateView.as_view(), name='plantilla_create'),
    path('plantillas/<int:pk>/editar/', views.PlantillaUpdateView.as_view(), name='plantilla_update'),
    path('plantillas/<int:pk>/eliminar/', views.PlantillaDeleteView.as_view(), name='plantilla_delete'),

    # Generar documento desde plantilla
    path('plantillas/<int:plantilla_pk>/generar/<int:proyecto_pk>/',
         views.GenerarDesdeProyectoView.as_view(), name='generar_desde_proyecto'),
    path('plantillas/<int:plantilla_pk>/generar/',
         views.GenerarStandaloneView.as_view(), name='generar_standalone'),

    # Documentos generados
    path('documentos/', views.DocumentoListView.as_view(), name='documento_list'),
    path('documentos/nuevo/', views.DocumentoCreateView.as_view(), name='documento_create'),
    path('documentos/<int:pk>/', views.DocumentoDetailView.as_view(), name='documento_detail'),
    path('documentos/<int:pk>/editar/', views.DocumentoUpdateView.as_view(), name='documento_update'),
    path('documentos/<int:pk>/eliminar/', views.DocumentoDeleteView.as_view(), name='documento_delete'),
    path('documentos/<int:pk>/imprimir/', views.DocumentoPrintView.as_view(), name='documento_print'),
    path('documentos/<int:pk>/vincular/', views.DocumentoVincularView.as_view(), name='documento_vincular'),

    # Repositorio de archivos
    path('repositorio/', views.RepositorioView.as_view(), name='repositorio'),
    path('repositorio/carpeta/nueva/', views.CarpetaCreateView.as_view(), name='carpeta_create'),
    path('repositorio/carpeta/<int:pk>/eliminar/', views.CarpetaDeleteView.as_view(), name='carpeta_delete'),
    path('repositorio/archivo/subir/', views.ArchivoSubirView.as_view(), name='archivo_subir'),
    path('repositorio/archivo/<int:pk>/eliminar/', views.ArchivoDeleteView.as_view(), name='archivo_delete'),
]
