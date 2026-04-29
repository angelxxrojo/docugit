from django.contrib import admin

from .models import DocumentoGenerado, PlantillaDocumento


@admin.register(PlantillaDocumento)
class PlantillaDocumentoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo', 'es_predeterminada', 'activo', 'creado_por']
    list_filter = ['tipo', 'activo', 'es_predeterminada']
    search_fields = ['nombre']


@admin.register(DocumentoGenerado)
class DocumentoGeneradoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo', 'empresa', 'proyecto', 'activo', 'created_at']
    list_filter = ['tipo', 'activo']
    search_fields = ['nombre']
    raw_id_fields = ['proyecto', 'empresa', 'plantilla_origen']
