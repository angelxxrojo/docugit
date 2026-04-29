from django.urls import path

from . import views

app_name = 'catalogo'

urlpatterns = [
    path('', views.CatalogoIndexView.as_view(), name='index'),

    # Categorías de servicio
    path('categorias/', views.CategoriaListView.as_view(), name='categoria_list'),
    path('categorias/nueva/', views.CategoriaCreateView.as_view(), name='categoria_create'),
    path('categorias/<int:pk>/editar/', views.CategoriaUpdateView.as_view(), name='categoria_update'),
    path('categorias/<int:pk>/eliminar/', views.CategoriaDeleteView.as_view(), name='categoria_delete'),

    # Servicios
    path('servicios/', views.ServicioListView.as_view(), name='servicio_list'),
    path('servicios/nuevo/', views.ServicioCreateView.as_view(), name='servicio_create'),
    path('servicios/<int:pk>/editar/', views.ServicioUpdateView.as_view(), name='servicio_update'),
    path('servicios/<int:pk>/eliminar/', views.ServicioDeleteView.as_view(), name='servicio_delete'),

    # Condiciones comerciales
    path('condiciones/', views.CondicionListView.as_view(), name='condicion_list'),
    path('condiciones/nueva/', views.CondicionCreateView.as_view(), name='condicion_create'),
    path('condiciones/<int:pk>/editar/', views.CondicionUpdateView.as_view(), name='condicion_update'),
    path('condiciones/<int:pk>/eliminar/', views.CondicionDeleteView.as_view(), name='condicion_delete'),

    # Cuentas bancarias
    path('cuentas/', views.CuentaListView.as_view(), name='cuenta_list'),
    path('cuentas/nueva/', views.CuentaCreateView.as_view(), name='cuenta_create'),
    path('cuentas/<int:pk>/editar/', views.CuentaUpdateView.as_view(), name='cuenta_update'),
    path('cuentas/<int:pk>/eliminar/', views.CuentaDeleteView.as_view(), name='cuenta_delete'),

    # Monedas
    path('monedas/', views.MonedaListView.as_view(), name='moneda_list'),
    path('monedas/nueva/', views.MonedaCreateView.as_view(), name='moneda_create'),
    path('monedas/<int:pk>/editar/', views.MonedaUpdateView.as_view(), name='moneda_update'),
    path('monedas/<int:pk>/desactivar/', views.MonedaDeleteView.as_view(), name='moneda_delete'),

    # Tipo de cambio
    path('tipo-cambio/', views.TipoCambioListView.as_view(), name='tipocambio_list'),
    path('tipo-cambio/nuevo/', views.TipoCambioCreateView.as_view(), name='tipocambio_create'),

    # Categorías de producto
    path('categorias-producto/', views.CategoriaProductoListView.as_view(), name='categoria_producto_list'),
    path('categorias-producto/nueva/', views.CategoriaProductoCreateView.as_view(), name='categoria_producto_create'),
    path('categorias-producto/<int:pk>/editar/', views.CategoriaProductoUpdateView.as_view(), name='categoria_producto_update'),
    path('categorias-producto/<int:pk>/eliminar/', views.CategoriaProductoDeleteView.as_view(), name='categoria_producto_delete'),

    # Productos
    path('productos/', views.ProductoListView.as_view(), name='producto_list'),
    path('productos/nuevo/', views.ProductoCreateView.as_view(), name='producto_create'),
    path('productos/<int:pk>/editar/', views.ProductoUpdateView.as_view(), name='producto_update'),
    path('productos/<int:pk>/eliminar/', views.ProductoDeleteView.as_view(), name='producto_delete'),
]
