from django.urls import path
from . import views

app_name = 'proformas'

urlpatterns = [
    path('', views.ProformaListView.as_view(), name='proforma_list'),
    path('nueva/', views.ProformaCreateView.as_view(), name='proforma_create'),
    path('<int:pk>/', views.ProformaDetailView.as_view(), name='proforma_detail'),
    path('<int:pk>/editar/', views.ProformaUpdateView.as_view(), name='proforma_update'),
    path('<int:pk>/eliminar/', views.ProformaDeleteView.as_view(), name='proforma_delete'),
    path('<int:pk>/estado/', views.ProformaEstadoView.as_view(), name='proforma_estado'),
    path('<int:pk>/margen/', views.ProformaMargenView.as_view(), name='proforma_margen'),
    path('<int:pk>/nueva-version/', views.ProformaNuevaVersionView.as_view(), name='proforma_nueva_version'),
    path('<int:pk>/pdf/', views.ProformaPDFView.as_view(), name='proforma_pdf'),
    # Items
    path('<int:proforma_pk>/items/', views.ProformaItemCreateView.as_view(), name='item_create'),
    path('<int:proforma_pk>/items/cancelar/', views.ProformaItemCancelEditView.as_view(), name='item_edit_cancel'),
    path('<int:proforma_pk>/items/<int:item_pk>/editar/', views.ProformaItemEditView.as_view(), name='item_edit'),
    path('<int:proforma_pk>/items/<int:item_pk>/eliminar/', views.ProformaItemDeleteView.as_view(), name='item_delete'),
    # Condiciones
    path('<int:proforma_pk>/condiciones/', views.ProformaCondicionCreateView.as_view(), name='condicion_create'),
    path('<int:proforma_pk>/condiciones/<int:cond_pk>/eliminar/', views.ProformaCondicionDeleteView.as_view(), name='condicion_delete'),
    # HTMX helpers
    path('htmx/contactos/', views.ContactosByEmpresaView.as_view(), name='htmx_contactos'),
    path('htmx/servicio/', views.ServicioDataView.as_view(), name='htmx_servicio'),
    path('htmx/condicion/', views.CondicionDataView.as_view(), name='htmx_condicion'),
    path('htmx/producto/', views.ProductoDataView.as_view(), name='htmx_producto'),
]
