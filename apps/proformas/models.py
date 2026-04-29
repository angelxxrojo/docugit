import datetime
from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel


class Proforma(TimeStampedModel):
    ESTADO_BORRADOR = 'borrador'
    ESTADO_ENVIADA = 'enviada'
    ESTADO_APROBADA = 'aprobada'
    ESTADO_RECHAZADA = 'rechazada'
    ESTADO_VENCIDA = 'vencida'

    ESTADO_CHOICES = [
        (ESTADO_BORRADOR, _('Borrador')),
        (ESTADO_ENVIADA, _('Enviada')),
        (ESTADO_APROBADA, _('Aprobada')),
        (ESTADO_RECHAZADA, _('Rechazada')),
        (ESTADO_VENCIDA, _('Vencida')),
    ]

    ESTADO_BADGE = {
        ESTADO_BORRADOR: 'bg-gray-100 text-gray-600',
        ESTADO_ENVIADA: 'bg-blue-100 text-blue-700',
        ESTADO_APROBADA: 'bg-green-100 text-green-700',
        ESTADO_RECHAZADA: 'bg-red-100 text-red-700',
        ESTADO_VENCIDA: 'bg-yellow-100 text-yellow-700',
    }

    numero = models.CharField(_('Número'), max_length=20, db_index=True)
    version = models.PositiveSmallIntegerField(_('Versión'), default=1)
    es_vigente = models.BooleanField(_('Versión vigente'), default=True)

    empresa = models.ForeignKey(
        'clientes.Empresa', on_delete=models.PROTECT,
        related_name='proformas', verbose_name=_('Empresa'),
    )
    contacto = models.ForeignKey(
        'clientes.Contacto', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='proformas', verbose_name=_('Contacto'),
    )
    sede = models.ForeignKey(
        'clientes.Sede', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='proformas', verbose_name=_('Sede'),
    )

    titulo = models.CharField(_('Asunto'), max_length=300)
    estado = models.CharField(
        _('Estado'), max_length=20, choices=ESTADO_CHOICES, default=ESTADO_BORRADOR,
    )

    tipo_cambio = models.ForeignKey(
        'catalogo.TipoCambio', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='proformas', verbose_name=_('Tipo de cambio'),
    )
    tc_venta = models.DecimalField(
        _('T.C. venta'), max_digits=10, decimal_places=4,
        null=True, blank=True,
        help_text=_('Valor snapshot al momento de crear la proforma'),
    )

    fecha_emision = models.DateField(_('Fecha de emisión'), default=datetime.date.today)
    validez_dias = models.PositiveSmallIntegerField(_('Validez (días)'), default=30)

    incluye_igv = models.BooleanField(_('Incluye IGV'), default=True)
    porcentaje_igv = models.DecimalField(
        _('% IGV'), max_digits=5, decimal_places=2, default=Decimal('18.00'),
    )

    subtotal_usd = models.DecimalField(_('Subtotal USD'), max_digits=14, decimal_places=2, default=0)
    igv_usd = models.DecimalField(_('IGV USD'), max_digits=14, decimal_places=2, default=0)
    total_usd = models.DecimalField(_('Total USD'), max_digits=14, decimal_places=2, default=0)
    subtotal_pen = models.DecimalField(_('Subtotal PEN'), max_digits=14, decimal_places=2, default=0)
    igv_pen = models.DecimalField(_('IGV PEN'), max_digits=14, decimal_places=2, default=0)
    total_pen = models.DecimalField(_('Total PEN'), max_digits=14, decimal_places=2, default=0)

    tecnico = models.ForeignKey(
        'usuarios.Usuario', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='proformas_preparadas',
        verbose_name=_('Técnico / Responsable'),
    )

    margen_objetivo = models.DecimalField(
        _('Margen objetivo (%)'), max_digits=5, decimal_places=2, default=Decimal('0'),
        help_text=_('% de ganancia que se aplicará al calcular precios sugeridos'),
    )
    observaciones = models.TextField(_('Observaciones'), blank=True)
    activo = models.BooleanField(_('Activo'), default=True)

    class Meta:
        verbose_name = _('Proforma')
        verbose_name_plural = _('Proformas')
        ordering = ['-created_at']
        unique_together = [['numero', 'version']]
        default_permissions = ()
        permissions = [
            ('ver_proformas',    'Ver lista de proformas'),
            ('crear_proforma',   'Crear proforma'),
            ('editar_proforma',  'Editar proforma'),
            ('eliminar_proforma','Archivar proforma'),
            ('ver_costos',       'Ver costos internos y rentabilidad'),
            ('exportar_pdf',     'Exportar PDF de proforma'),
        ]

    def __str__(self):
        return f"{self.numero} v{self.version} — {self.empresa.nombre_display}"

    @property
    def fecha_vencimiento(self):
        return self.fecha_emision + datetime.timedelta(days=self.validez_dias)

    @property
    def estado_badge_class(self):
        return self.ESTADO_BADGE.get(self.estado, 'bg-gray-100 text-gray-600')

    def recalcular_totales(self):
        items = self.items.all()
        subtotal = sum(
            (item.cantidad * item.precio_usd) for item in items
        ) or Decimal('0')
        igv = (subtotal * self.porcentaje_igv / 100).quantize(Decimal('0.01')) if self.incluye_igv else Decimal('0')
        total = (subtotal + igv).quantize(Decimal('0.01'))
        subtotal = subtotal.quantize(Decimal('0.01'))
        self.subtotal_usd = subtotal
        self.igv_usd = igv
        self.total_usd = total
        if self.tc_venta:
            self.subtotal_pen = (subtotal * self.tc_venta).quantize(Decimal('0.01'))
            self.igv_pen = (igv * self.tc_venta).quantize(Decimal('0.01'))
            self.total_pen = (total * self.tc_venta).quantize(Decimal('0.01'))
        else:
            self.subtotal_pen = Decimal('0')
            self.igv_pen = Decimal('0')
            self.total_pen = Decimal('0')
        self.save(update_fields=[
            'subtotal_usd', 'igv_usd', 'total_usd',
            'subtotal_pen', 'igv_pen', 'total_pen',
        ])

    @classmethod
    def generar_numero(cls):
        from django.utils import timezone
        year = timezone.now().year
        prefix = f"PROF-{year}-"
        last = (
            cls.objects
            .filter(numero__startswith=prefix)
            .order_by('-numero')
            .values_list('numero', flat=True)
            .first()
        )
        if last:
            try:
                seq = int(last.replace(prefix, '')) + 1
            except ValueError:
                seq = 1
        else:
            seq = 1
        return f"{prefix}{seq:04d}"


class ProformaItem(models.Model):
    UNIDAD_CHOICES = [
        ('servicio', 'Servicio'),
        ('hora', 'Hora'),
        ('punto', 'Punto'),
        ('mes', 'Mes'),
        ('dia', 'Día'),
        ('km', 'Kilómetro'),
        ('unidad', 'Unidad'),
        ('par', 'Par'),
        ('rollo', 'Rollo'),
        ('metro', 'Metro'),
        ('kit', 'Kit'),
        ('caja', 'Caja'),
        ('licencia', 'Licencia'),
        ('global', 'Global'),
    ]

    proforma = models.ForeignKey(
        Proforma, on_delete=models.CASCADE, related_name='items',
    )
    orden = models.PositiveSmallIntegerField(_('Orden'), default=0)
    servicio = models.ForeignKey(
        'catalogo.Servicio', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='proforma_items',
        verbose_name=_('Servicio del catálogo'),
    )
    producto = models.ForeignKey(
        'catalogo.Producto', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='proforma_items',
        verbose_name=_('Producto del catálogo'),
    )
    descripcion = models.CharField(_('Descripción'), max_length=300)
    descripcion_tecnica = models.TextField(_('Descripción técnica'), blank=True)
    unidad = models.CharField(
        _('Unidad'), max_length=20, choices=UNIDAD_CHOICES, default='servicio',
    )
    cantidad = models.DecimalField(
        _('Cantidad'), max_digits=10, decimal_places=2, default=1,
    )
    precio_usd = models.DecimalField(
        _('Precio USD'), max_digits=10, decimal_places=2,
    )
    costo = models.DecimalField(
        _('Costo Gibit'), max_digits=10, decimal_places=2,
        null=True, blank=True,
    )
    moneda_costo = models.CharField(
        _('Moneda del costo'), max_length=5,
        choices=[('USD', 'USD'), ('PEN', 'S/')],
        default='USD',
    )

    class Meta:
        verbose_name = _('Ítem de proforma')
        verbose_name_plural = _('Ítems de proforma')
        ordering = ['orden', 'id']

    def __str__(self):
        return f"{self.descripcion} x{self.cantidad}"

    @property
    def subtotal_usd(self):
        return (self.cantidad * self.precio_usd).quantize(Decimal('0.01'))


class ProformaCondicion(models.Model):
    proforma = models.ForeignKey(
        Proforma, on_delete=models.CASCADE, related_name='condiciones',
    )
    condicion_ref = models.ForeignKey(
        'catalogo.CondicionComercial', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='proforma_condiciones',
        verbose_name=_('Condición de catálogo'),
    )
    orden = models.PositiveSmallIntegerField(_('Orden'), default=0)
    titulo = models.CharField(_('Título'), max_length=150)
    contenido = models.TextField(_('Contenido'))

    class Meta:
        verbose_name = _('Condición de proforma')
        verbose_name_plural = _('Condiciones de proforma')
        ordering = ['orden', 'id']

    def __str__(self):
        return self.titulo
