import logging

from django.http import HttpRequest, JsonResponse
from django.views import View

from apps.location import models

logger = logging.getLogger(__name__)


class GetProvinceView(View):
    """
    Vista AJAX para obtener provincias por departamento.
    Parte del sistema de selects en cascada para ubicación.
    """

    def get(self, request: HttpRequest) -> JsonResponse:
        """
        Get provinces for a department.

        Args:
            request: HTTP request with department_id

        Returns:
            JsonResponse: List of provinces
        """
        department_id = request.GET.get("department_id")

        if not department_id:
            return JsonResponse([], safe=False)

        try:
            provinces = (
                models.Province.objects.filter(department_id=department_id)
                .values("ubigeo_id", "name")
                .order_by("name")
            )
            return JsonResponse({"provinces": list(provinces)})
        except Exception as e:
            logger.error(f"Error getting provinces: {str(e)}")
            return JsonResponse([], safe=False)


class GetDistrictView(View):
    """
    Vista AJAX para obtener distritos por provincia.
    Parte del sistema de selects en cascada para ubicación.
    """

    def get(self, request: HttpRequest) -> JsonResponse:
        """
        Get districts for a province.

        Args:
            request: HTTP request with province_id

        Returns:
            JsonResponse: List of districts
        """
        province_id = request.GET.get("province_id")

        if not province_id:
            return JsonResponse([], safe=False)

        try:
            districts = (
                models.District.objects.filter(province_id=province_id)
                .values("ubigeo_id", "name")
                .order_by("name")
            )
            return JsonResponse({"districts": list(districts)})
        except Exception as e:
            logger.error(f"Error getting districts: {str(e)}")
            return JsonResponse([], safe=False)
