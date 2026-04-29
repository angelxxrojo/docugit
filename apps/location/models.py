from django.db import models


class Country(models.Model):
    code = models.CharField(max_length=2, primary_key=True)
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Countries"

    def __str__(self):
        return self.name


class Department(models.Model):
    ubigeo_id = models.CharField(max_length=2, primary_key=True)
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"

    def __str__(self):
        return self.name


class Province(models.Model):
    ubigeo_id = models.CharField(max_length=4, primary_key=True)
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Province"
        verbose_name_plural = "Provinces"

    def __str__(self):
        return self.name


class District(models.Model):
    ubigeo_id = models.CharField(max_length=6, primary_key=True)
    name = models.CharField(max_length=100)
    province = models.ForeignKey(Province, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "District"
        verbose_name_plural = "Districts"

    def __str__(self):
        return self.name


class GeographicLocationMixin(models.Model):
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        default="PE",  # Perú by default using country code
        verbose_name="Country",
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        verbose_name="Department",
        null=True,
        blank=True,
    )
    province = models.ForeignKey(
        Province,
        on_delete=models.PROTECT,
        verbose_name="Province",
        null=True,
        blank=True,
    )
    district = models.ForeignKey(
        District,
        on_delete=models.PROTECT,
        verbose_name="District",
        null=True,
        blank=True,
    )
    address = models.CharField(max_length=255, verbose_name="Address", blank=True)
    code_postal = models.CharField(
        max_length=10, verbose_name="Postal Code", blank=True
    )

    class Meta:
        abstract = True
