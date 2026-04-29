from django.urls import path

from apps.location import views

app_name = "location"


urlpatterns = [
    # AJAX endpoints - Ubicación (selects en cascada)
    path("api/provinces/", views.GetProvinceView.as_view(), name="get_provinces"),
    path("api/districts/", views.GetDistrictView.as_view(), name="get_districts"),
]
