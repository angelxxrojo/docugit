from django.contrib import admin

from .models import Documento, Proyecto, TecnicoAsignado


class TecnicoAsignadoInline(admin.TabularInline):
    model = TecnicoAsignado
    extra = 0


class DocumentoInline(admin.TabularInline):
    model = Documento
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ['numero', 'titulo', 'empresa', 'estado', 'fecha_inicio', 'fecha_fin_prevista', 'valor_usd', 'activo']
    list_filter = ['estado', 'activo']
    search_fields = ['numero', 'titulo', 'empresa__razon_social']
    inlines = [TecnicoAsignadoInline, DocumentoInline]
    readonly_fields = ['numero', 'created_at', 'updated_at']


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo', 'proyecto', 'tecnico', 'fecha_vencimiento', 'activo']
    list_filter = ['tipo', 'activo']
    search_fields = ['titulo', 'proyecto__numero']
