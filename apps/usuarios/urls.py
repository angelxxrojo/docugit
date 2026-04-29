from django.urls import path

from . import views

app_name = 'usuarios'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('perfil/', views.PerfilView.as_view(), name='perfil'),
    # Usuarios
    path('usuarios/', views.UsuarioListView.as_view(), name='usuario_list'),
    path('usuarios/nuevo/', views.UsuarioCreateView.as_view(), name='usuario_create'),
    path('usuarios/<int:pk>/editar/', views.UsuarioUpdateView.as_view(), name='usuario_update'),
    path('usuarios/<int:pk>/toggle/', views.UsuarioToggleView.as_view(), name='usuario_toggle'),
    # Roles
    path('roles/', views.RolListView.as_view(), name='rol_list'),
    path('roles/nuevo/', views.RolCreateView.as_view(), name='rol_create'),
    path('roles/<int:pk>/editar/', views.RolUpdateView.as_view(), name='rol_update'),
]
