from django.urls import path

from . import views

app_name = 'clientes'

urlpatterns = [
    # Empresa
    path('', views.EmpresaListView.as_view(), name='empresa_list'),
    path('nueva/', views.EmpresaCreateView.as_view(), name='empresa_create'),
    path('<int:pk>/', views.EmpresaDetailView.as_view(), name='empresa_detail'),
    path('<int:pk>/editar/', views.EmpresaUpdateView.as_view(), name='empresa_update'),
    path('<int:pk>/eliminar/', views.EmpresaDeleteView.as_view(), name='empresa_delete'),

    # Sede (anidada bajo empresa)
    path('<int:empresa_pk>/sedes/nueva/', views.SedeCreateView.as_view(), name='sede_create'),
    path('<int:empresa_pk>/sedes/<int:pk>/editar/', views.SedeUpdateView.as_view(), name='sede_update'),
    path('<int:empresa_pk>/sedes/<int:pk>/eliminar/', views.SedeDeleteView.as_view(), name='sede_delete'),

    # Contacto (anidado bajo empresa)
    path('<int:empresa_pk>/contactos/nuevo/', views.ContactoCreateView.as_view(), name='contacto_create'),
    path('<int:empresa_pk>/contactos/<int:pk>/editar/', views.ContactoUpdateView.as_view(), name='contacto_update'),
    path('<int:empresa_pk>/contactos/<int:pk>/eliminar/', views.ContactoDeleteView.as_view(), name='contacto_delete'),
]
