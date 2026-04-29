from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel


class CategoriaServicio(TimeStampedModel):
    nombre = models.CharField(_('Nombre'), max_length=100, unique=True)
    descripcion = models.CharField(_('Descripción'), max_length=255, blank=True)
    activo = models.BooleanField(_('Activa'), default=True)

    class Meta:
        verbose_name = _('Categoría de servicio')
        verbose_name_plural = _('Categorías de servicio')
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Servicio(TimeStampedModel):
    UNIDAD_CHOICES = [
        ('servicio', 'Servicio'),
        ('hora', 'Hora'),
        ('punto', 'Punto'),
        ('mes', 'Mes'),
        ('dia', 'Día'),
        ('km', 'Kilómetro'),
        ('unidad', 'Unidad'),
    ]

    categoria = models.ForeignKey(
        CategoriaServicio, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='servicios',
        verbose_name=_('Categoría'),
    )
    codigo = models.CharField(_('Código'), max_length=20, blank=True)
    nombre = models.CharField(_('Nombre'), max_length=200)
    descripcion = models.TextField(_('Descripción técnica'), blank=True)
    unidad = models.CharField(_('Unidad'), max_length=20, choices=UNIDAD_CHOICES, default='servicio')
    precio_usd = models.DecimalField(_('Precio (USD)'), max_digits=10, decimal_places=2, default=0)
    costo = models.DecimalField(
        _('Costo Gibit'), max_digits=10, decimal_places=2,
        null=True, blank=True,
        help_text=_('Costo interno / lo que cobra el proveedor. Opcional.'),
    )
    moneda_costo = models.CharField(
        _('Moneda del costo'), max_length=5,
        choices=[('USD', 'USD'), ('PEN', 'S/')],
        default='USD',
    )
    activo = models.BooleanField(_('Activo'), default=True)

    class Meta:
        verbose_name = _('Servicio')
        verbose_name_plural = _('Servicios')
        ordering = ['categoria__nombre', 'nombre']
        default_permissions = ()
        permissions = [
            ('ver_catalogo',           'Ver catálogo'),
            ('gestionar_servicios',    'Gestionar servicios'),
            ('gestionar_productos',    'Gestionar productos'),
            ('gestionar_categorias',   'Gestionar categorías'),
            ('gestionar_condiciones',  'Gestionar condiciones comerciales'),
            ('gestionar_cuentas',      'Gestionar cuentas bancarias'),
            ('gestionar_tipos_cambio', 'Gestionar tipos de cambio y monedas'),
        ]

    def __str__(self):
        return f"{self.codigo} — {self.nombre}" if self.codigo else self.nombre


class CondicionComercial(TimeStampedModel):
    TIPO_CHOICES = [
        ('pago', 'Condiciones de pago'),
        ('viatico', 'Viáticos'),
        ('plazo', 'Plazo de entrega'),
        ('garantia', 'Garantía'),
        ('alcance', 'Alcance del servicio'),
        ('otro', 'Otro'),
    ]

    nombre = models.CharField(_('Nombre'), max_length=150)
    tipo = models.CharField(_('Tipo'), max_length=20, choices=TIPO_CHOICES, default='otro')
    contenido = models.TextField(_('Contenido'))
    es_default = models.BooleanField(_('Incluir por defecto en proformas'), default=False)
    orden = models.PositiveSmallIntegerField(_('Orden'), default=0)
    activo = models.BooleanField(_('Activa'), default=True)

    class Meta:
        verbose_name = _('Condición comercial')
        verbose_name_plural = _('Condiciones comerciales')
        ordering = ['orden', 'tipo', 'nombre']

    def __str__(self):
        return f"{self.get_tipo_display()} — {self.nombre}"


class CuentaBancaria(TimeStampedModel):
    BANCO_CHOICES = [
        ('BCP', 'BCP'),
        ('BBVA', 'BBVA'),
        ('INTERBANK', 'Interbank'),
        ('SCOTIABANK', 'Scotiabank'),
        ('BN', 'Banco de la Nación'),
        ('BANBIF', 'BanBif'),
        ('OTRO', 'Otro'),
    ]
    MONEDA_CHOICES = [
        ('PEN', 'Soles (S/)'),
        ('USD', 'Dólares ($)'),
    ]

    banco = models.CharField(_('Banco'), max_length=20, choices=BANCO_CHOICES)
    moneda = models.CharField(_('Moneda'), max_length=3, choices=MONEDA_CHOICES, default='PEN')
    numero_cuenta = models.CharField(_('Número de cuenta'), max_length=30)
    cci = models.CharField(_('CCI'), max_length=30, blank=True)
    titular = models.CharField(_('Titular'), max_length=200)
    es_detraccion = models.BooleanField(_('Es cuenta de detracciones'), default=False)
    porcentaje_detraccion = models.DecimalField(
        _('% Detracción'), max_digits=5, decimal_places=2,
        null=True, blank=True,
        help_text=_('Solo si es cuenta de detracciones (Ej: 4.00)'),
    )
    activo = models.BooleanField(_('Activa'), default=True)

    class Meta:
        verbose_name = _('Cuenta bancaria')
        verbose_name_plural = _('Cuentas bancarias')
        ordering = ['banco', 'moneda']

    def __str__(self):
        simbolo = 'S/' if self.moneda == 'PEN' else '$'
        return f"{self.get_banco_display()} {simbolo} — {self.numero_cuenta}"


class CategoriaProducto(TimeStampedModel):
    nombre = models.CharField(_('Nombre'), max_length=100, unique=True)
    descripcion = models.CharField(_('Descripción'), max_length=255, blank=True)
    activo = models.BooleanField(_('Activa'), default=True)

    class Meta:
        verbose_name = _('Categoría de producto')
        verbose_name_plural = _('Categorías de producto')
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Producto(TimeStampedModel):
    UNIDAD_CHOICES = [
        ('unidad', 'Unidad'),
        ('par', 'Par'),
        ('rollo', 'Rollo'),
        ('metro', 'Metro'),
        ('kit', 'Kit'),
        ('caja', 'Caja'),
        ('licencia', 'Licencia'),
        ('global', 'Global'),
    ]

    categoria = models.ForeignKey(
        CategoriaProducto, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='productos',
        verbose_name=_('Categoría'),
    )
    nombre = models.CharField(_('Nombre'), max_length=200)
    marca = models.CharField(_('Marca'), max_length=100, blank=True)
    modelo = models.CharField(_('Modelo'), max_length=150, blank=True, db_index=True,
                               help_text=_('Código de modelo del fabricante. Facilita búsqueda e importación.'))
    descripcion = models.TextField(_('Especificaciones técnicas'), blank=True)
    unidad = models.CharField(_('Unidad'), max_length=20, choices=UNIDAD_CHOICES, default='unidad')
    precio_usd = models.DecimalField(_('Precio (USD)'), max_digits=10, decimal_places=2, default=0)
    costo = models.DecimalField(
        _('Costo Gibit'), max_digits=10, decimal_places=2,
        null=True, blank=True,
        help_text=_('Costo de compra / proveedor. Opcional.'),
    )
    moneda_costo = models.CharField(
        _('Moneda del costo'), max_length=5,
        choices=[('USD', 'USD'), ('PEN', 'S/')],
        default='USD',
    )
    activo = models.BooleanField(_('Activo'), default=True)

    class Meta:
        verbose_name = _('Producto')
        verbose_name_plural = _('Productos')
        ordering = ['categoria__nombre', 'nombre']

    def __str__(self):
        partes = []
        if self.marca:
            partes.append(self.marca)
        partes.append(self.nombre)
        if self.modelo:
            partes.append(f'[{self.modelo}]')
        return ' '.join(partes)

    @property
    def display_nombre(self):
        return self.nombre

    @property
    def descripcion_proforma(self):
        """Texto sugerido para descripcion_tecnica de un ProformaItem."""
        lines = [f'• {self.nombre}']
        if self.modelo:
            lines.append(f'• Modelo: {self.modelo}')
        if self.descripcion:
            for line in self.descripcion.strip().splitlines():
                if line.strip():
                    lines.append(f'• {line.strip()}')
        return '\n'.join(lines)


class Moneda(TimeStampedModel):
    codigo = models.CharField(_('Código'), max_length=5, unique=True)
    nombre = models.CharField(_('Nombre'), max_length=100)
    simbolo = models.CharField(_('Símbolo'), max_length=5)
    activo = models.BooleanField(_('Activa'), default=True)

    class Meta:
        verbose_name = _('Moneda')
        verbose_name_plural = _('Monedas')
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} — {self.nombre}"


class TipoCambio(TimeStampedModel):
    moneda = models.ForeignKey(
        Moneda, on_delete=models.PROTECT,
        related_name='tipos_cambio',
        verbose_name=_('Moneda'),
    )
    compra = models.DecimalField(_('Compra'), max_digits=10, decimal_places=4)
    venta = models.DecimalField(_('Venta'), max_digits=10, decimal_places=4)
    nota = models.CharField(_('Nota'), max_length=200, blank=True,
                            help_text=_('Ej: Fuente SBS, ajuste por cierre de mes'))

    class Meta:
        verbose_name = _('Tipo de cambio')
        verbose_name_plural = _('Tipos de cambio')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.moneda.codigo} {self.moneda.simbolo}{self.venta} — {self.created_at.strftime('%d/%m/%Y %H:%M')}"

    @classmethod
    def get_vigente(cls, codigo='USD'):
        return cls.objects.filter(moneda__codigo=codigo, moneda__activo=True).first()

    @classmethod
    def get_vigentes(cls):
        from django.db.models import Max
        latest_ids = (
            cls.objects
            .filter(moneda__activo=True)
            .values('moneda')
            .annotate(latest_id=Max('id'))
            .values_list('latest_id', flat=True)
        )
        return cls.objects.filter(id__in=latest_ids).select_related('moneda').order_by('moneda__codigo')
