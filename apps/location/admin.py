from django.contrib import admin

from .models import Country, Department, District, Province


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    """Admin configuration for Country model."""

    list_display = ("code", "name")
    list_display_links = ("code", "name")
    search_fields = ("code", "name")
    ordering = ("name",)

    fieldsets = (("Basic Information", {"fields": ("code", "name")}),)

    def get_queryset(self, request):
        """Return queryset with optimized queries."""
        return super().get_queryset(request).select_related()


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """Admin configuration for Department model."""

    list_display = ("ubigeo_id", "name", "country")
    list_display_links = ("ubigeo_id", "name")
    list_filter = ("country",)
    search_fields = ("ubigeo_id", "name", "country__name")
    ordering = ("country__name", "name")

    fieldsets = (
        ("Basic Information", {"fields": ("ubigeo_id", "name")}),
        ("Geographic Information", {"fields": ("country",)}),
    )

    def get_queryset(self, request):
        """Return queryset with optimized queries."""
        return super().get_queryset(request).select_related("country")


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    """Admin configuration for Province model."""

    list_display = ("ubigeo_id", "name", "department", "country_display")
    list_display_links = ("ubigeo_id", "name")
    list_filter = ("department__country", "department")
    search_fields = (
        "ubigeo_id",
        "name",
        "department__name",
        "department__country__name",
    )
    ordering = ("department__country__name", "department__name", "name")

    fieldsets = (
        ("Basic Information", {"fields": ("ubigeo_id", "name")}),
        ("Geographic Information", {"fields": ("department",)}),
    )

    def country_display(self, obj):
        """Display country name for the province."""
        return obj.department.country.name if obj.department else "-"

    country_display.short_description = "Country"
    country_display.admin_order_field = "department__country__name"

    def get_queryset(self, request):
        """Return queryset with optimized queries."""
        return super().get_queryset(request).select_related("department__country")


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    """Admin configuration for District model."""

    list_display = (
        "ubigeo_id",
        "name",
        "province",
        "department_display",
        "country_display",
    )
    list_display_links = ("ubigeo_id", "name")
    list_filter = (
        "province__department__country",
        "province__department",
        "province",
    )
    search_fields = (
        "ubigeo_id",
        "name",
        "province__name",
        "province__department__name",
        "province__department__country__name",
    )
    ordering = (
        "province__department__country__name",
        "province__department__name",
        "province__name",
        "name",
    )

    fieldsets = (
        ("Basic Information", {"fields": ("ubigeo_id", "name")}),
        ("Geographic Information", {"fields": ("province",)}),
    )

    def department_display(self, obj):
        """Display department name for the district."""
        return obj.province.department.name if obj.province else "-"

    department_display.short_description = "Department"
    department_display.admin_order_field = "province__department__name"

    def country_display(self, obj):
        """Display country name for the district."""
        if obj.province and obj.province.department:
            return obj.province.department.country.name
        return "-"

    country_display.short_description = "Country"
    country_display.admin_order_field = "province__department__country__name"

    def get_queryset(self, request):
        """Return queryset with optimized queries."""
        return (
            super()
            .get_queryset(request)
            .select_related("province__department__country")
        )


# Customize admin site
admin.site.site_header = "Location Management"
admin.site.site_title = "Location Admin"
admin.site.index_title = "Welcome to Location Management Portal"
