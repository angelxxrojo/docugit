from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel
from apps.location.models import GeographicLocationMixin


class Empresa(TimeStampedModel, GeographicLocationMixin):
    ruc = models.CharField(_('RUC'), max_length=11, unique=True)
    razon_social = models.CharField(_('Razón social'), max_length=200)
    nombre_comercial = models.CharField(_('Nombre comercial'), max_length=200, blank=True)
    sector = models.CharField(_('Sector'), max_length=100, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Empresa')
        verbose_name_plural = _('Empresas')
        ordering = ['razon_social']
        default_permissions = ()
        permissions = [
            ('ver_clientes',        'Ver lista de clientes'),
            ('crear_cliente',       'Crear cliente'),
            ('editar_cliente',      'Editar cliente'),
            ('eliminar_cliente',    'Archivar cliente'),
            ('gestionar_contactos', 'Gestionar contactos y sedes'),
        ]

    def __str__(self):
        return f"{self.ruc} - {self.razon_social}"

    @property
    def nombre_display(self):
        return self.nombre_comercial or self.razon_social


class Sede(TimeStampedModel, GeographicLocationMixin):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='sedes')
    nombre = models.CharField(_('Nombre'), max_length=100)
    referencia = models.TextField(_('Referencia'), blank=True)
    es_principal = models.BooleanField(_('Sede principal'), default=False)
    activo = models.BooleanField(_('Activa'), default=True)

    class Meta:
        verbose_name = _('Sede')
        verbose_name_plural = _('Sedes')
        ordering = ['-es_principal', 'nombre']

    def __str__(self):
        return f"{self.nombre} — {self.empresa.razon_social}"

    def save(self, *args, **kwargs):
        if self.es_principal:
            Sede.objects.filter(
                empresa=self.empresa, es_principal=True
            ).exclude(pk=self.pk).update(es_principal=False)
        super().save(*args, **kwargs)


class Contacto(TimeStampedModel):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='contactos')
    nombre = models.CharField(_('Nombre'), max_length=150)
    cargo = models.CharField(_('Cargo'), max_length=100)
    correo = models.EmailField(_('Correo'))
    whatsapp = models.CharField(_('WhatsApp'), max_length=20)
    es_principal = models.BooleanField(_('Contacto principal'), default=False)
    recibe_proforma = models.BooleanField(_('Recibe proformas'), default=True)
    recibe_informe = models.BooleanField(_('Recibe informes técnicos'), default=False)
    activo = models.BooleanField(_('Activo'), default=True)

    class Meta:
        verbose_name = _('Contacto')
        verbose_name_plural = _('Contactos')
        ordering = ['-es_principal', 'nombre']

    def __str__(self):
        return f"{self.nombre} ({self.cargo}) — {self.empresa.razon_social}"

    def save(self, *args, **kwargs):
        if self.es_principal:
            Contacto.objects.filter(
                empresa=self.empresa, es_principal=True
            ).exclude(pk=self.pk).update(es_principal=False)
        super().save(*args, **kwargs)
