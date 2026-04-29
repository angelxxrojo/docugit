from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('configuracion/', views.ConfiguracionView.as_view(), name='configuracion'),
]
