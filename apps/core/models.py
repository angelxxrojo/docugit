from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Configuracion(models.Model):
    """Singleton — siempre pk=1. Datos de la empresa para PDFs y cabeceras."""
    nombre_empresa = models.CharField('Nombre empresa', max_length=200, default='Gibit Tecnología')
    ruc = models.CharField('RUC', max_length=11, blank=True)
    direccion = models.CharField('Dirección', max_length=300, blank=True)
    telefono = models.CharField('Teléfono', max_length=50, blank=True)
    email = models.EmailField('Email', blank=True)
    web = models.CharField('Sitio web', max_length=100, blank=True)
    logo = models.ImageField('Logo', upload_to='config/', null=True, blank=True)
    slogan = models.CharField('Slogan / Descripción', max_length=150, blank=True)

    class Meta:
        verbose_name = 'Configuración'
        verbose_name_plural = 'Configuración'
        default_permissions = ()
        permissions = [
            ('ver_configuracion',   'Ver configuración del sistema'),
            ('editar_configuracion','Editar configuración del sistema'),
        ]

    def __str__(self):
        return self.nombre_empresa

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1, defaults={'nombre_empresa': 'Gibit Tecnología'})
        return obj
