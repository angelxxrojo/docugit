from django.contrib import admin
from .models import Proforma, ProformaItem, ProformaCondicion


class ProformaItemInline(admin.TabularInline):
    model = ProformaItem
    extra = 0
    readonly_fields = ['subtotal_usd']


class ProformaCondicionInline(admin.TabularInline):
    model = ProformaCondicion
    extra = 0


@admin.register(Proforma)
class ProformaAdmin(admin.ModelAdmin):
    list_display = ['numero', 'version', 'empresa', 'estado', 'total_usd', 'fecha_emision', 'activo']
    list_filter = ['estado', 'activo', 'es_vigente']
    search_fields = ['numero', 'empresa__razon_social', 'titulo']
    readonly_fields = ['numero', 'created_at', 'updated_at']
    inlines = [ProformaItemInline, ProformaCondicionInline]
    ordering = ['-created_at']
