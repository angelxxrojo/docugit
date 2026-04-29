from django.contrib import admin

from .models import Contacto, Empresa, Sede


class SedeInline(admin.TabularInline):
    model = Sede
    extra = 0
    fields = ['nombre', 'department', 'province', 'district', 'address', 'es_principal']


class ContactoInline(admin.TabularInline):
    model = Contacto
    extra = 0
    fields = ['nombre', 'cargo', 'correo', 'whatsapp', 'es_principal']


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ['ruc', 'razon_social', 'nombre_comercial', 'sector', 'activo', 'created_at']
    list_filter = ['activo', 'sector']
    search_fields = ['ruc', 'razon_social', 'nombre_comercial']
    inlines = [SedeInline, ContactoInline]


@admin.register(Sede)
class SedeAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'empresa', 'district', 'province', 'department', 'es_principal']
    list_filter = ['department', 'es_principal']
    search_fields = ['nombre', 'empresa__razon_social', 'district__name', 'address']
    autocomplete_fields = ['department', 'province', 'district']


@admin.register(Contacto)
class ContactoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'cargo', 'empresa', 'correo', 'whatsapp', 'es_principal']
    list_filter = ['es_principal', 'recibe_proforma', 'recibe_informe']
    search_fields = ['nombre', 'empresa__razon_social', 'correo']
