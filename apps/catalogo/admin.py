from django.contrib import admin

from .models import (
    CategoriaProducto, CategoriaServicio, CondicionComercial,
    CuentaBancaria, Moneda, Producto, Servicio, TipoCambio,
)


@admin.register(CategoriaServicio)
class CategoriaServicioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion', 'activo']
    search_fields = ['nombre']


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'categoria', 'unidad', 'precio_usd', 'activo']
    list_filter = ['activo', 'categoria', 'unidad']
    search_fields = ['nombre', 'codigo']


@admin.register(CondicionComercial)
class CondicionComercialAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo', 'es_default', 'orden', 'activo']
    list_filter = ['tipo', 'es_default', 'activo']


@admin.register(CuentaBancaria)
class CuentaBancariaAdmin(admin.ModelAdmin):
    list_display = ['banco', 'moneda', 'numero_cuenta', 'titular', 'es_detraccion', 'activo']
    list_filter = ['banco', 'moneda', 'es_detraccion', 'activo']


@admin.register(Moneda)
class MonedaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'simbolo', 'activo']
    list_filter = ['activo']


@admin.register(TipoCambio)
class TipoCambioAdmin(admin.ModelAdmin):
    list_display = ['moneda', 'compra', 'venta', 'created_at']
    list_filter = ['moneda']
    ordering = ['-created_at']


@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion', 'activo']
    search_fields = ['nombre']
    list_filter = ['activo']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'marca', 'modelo', 'categoria', 'unidad', 'precio_usd', 'activo']
    list_filter = ['activo', 'categoria', 'unidad']
    search_fields = ['nombre', 'marca', 'modelo']
