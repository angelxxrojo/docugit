import datetime
import os
from decimal import Decimal

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel


class Proyecto(TimeStampedModel):
    ESTADO_BORRADOR = 'borrador'
    ESTADO_PENDIENTE_FIRMA = 'pendiente_firma'
    ESTADO_ACTIVO = 'activo'
    ESTADO_EN_EJECUCION = 'en_ejecucion'
    ESTADO_COMPLETADO = 'completado'
    ESTADO_CANCELADO = 'cancelado'

    ESTADO_CHOICES = [
        (ESTADO_BORRADOR, _('Borrador')),
        (ESTADO_PENDIENTE_FIRMA, _('Pendiente de firma')),
        (ESTADO_ACTIVO, _('Activo')),
        (ESTADO_EN_EJECUCION, _('En ejecución')),
        (ESTADO_COMPLETADO, _('Completado')),
        (ESTADO_CANCELADO, _('Cancelado')),
    ]

    ESTADO_BADGE = {
        ESTADO_BORRADOR: 'bg-gray-100 text-gray-600',
        ESTADO_PENDIENTE_FIRMA: 'bg-yellow-100 text-yellow-700',
        ESTADO_ACTIVO: 'bg-blue-100 text-blue-700',
        ESTADO_EN_EJECUCION: 'bg-indigo-100 text-indigo-700',
        ESTADO_COMPLETADO: 'bg-green-100 text-green-700',
        ESTADO_CANCELADO: 'bg-red-100 text-red-700',
    }

    numero = models.CharField(_('Número'), max_length=20, db_index=True, unique=True)
    proforma = models.ForeignKey(
        'proformas.Proforma', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='proyectos',
        verbose_name=_('Proforma origen'),
    )
    empresa = models.ForeignKey(
        'clientes.Empresa', on_delete=models.PROTECT,
        related_name='proyectos', verbose_name=_('Empresa'),
    )
    contacto = models.ForeignKey(
        'clientes.Contacto', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='proyectos', verbose_name=_('Contacto'),
    )
    sede = models.ForeignKey(
        'clientes.Sede', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='proyectos', verbose_name=_('Sede'),
    )

    titulo = models.CharField(_('Título / Alcance'), max_length=300)
    estado = models.CharField(
        _('Estado'), max_length=20, choices=ESTADO_CHOICES, default=ESTADO_BORRADOR,
    )

    fecha_inicio = models.DateField(_('Fecha de inicio'), null=True, blank=True)
    fecha_fin_prevista = models.DateField(_('Fecha fin prevista'), null=True, blank=True)
    fecha_fin_real = models.DateField(_('Fecha fin real'), null=True, blank=True)

    valor_usd = models.DecimalField(
        _('Valor (USD)'), max_digits=14, decimal_places=2, default=Decimal('0'),
    )
    valor_pen = models.DecimalField(
        _('Valor (PEN)'), max_digits=14, decimal_places=2, default=Decimal('0'),
    )
    tc_venta = models.DecimalField(
        _('T.C. venta'), max_digits=10, decimal_places=4,
        null=True, blank=True,
        help_text=_('Tipo de cambio al momento de crear el proyecto'),
    )

    observaciones = models.TextField(_('Observaciones'), blank=True)
    texto_contrato = models.TextField(
        _('Texto del contrato'), blank=True,
        help_text=_('Cláusulas y condiciones adicionales para el contrato imprimible'),
    )
    activo = models.BooleanField(_('Activo'), default=True)

    class Meta:
        verbose_name = _('Proyecto')
        verbose_name_plural = _('Proyectos')
        ordering = ['-created_at']
        default_permissions = ()
        permissions = [
            ('ver_proyectos',        'Ver lista de proyectos'),
            ('crear_proyecto',       'Crear proyecto'),
            ('editar_proyecto',      'Editar proyecto'),
            ('eliminar_proyecto',    'Archivar proyecto'),
            ('ver_actividades',      'Ver actividades / Kanban'),
            ('gestionar_actividades','Crear y editar actividades'),
        ]

    def __str__(self):
        return f"{self.numero} — {self.titulo}"

    @classmethod
    def generar_numero(cls):
        year = timezone.now().year
        prefix = f"PROY-{year}-"
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

    @property
    def estado_badge_class(self):
        return self.ESTADO_BADGE.get(self.estado, 'bg-gray-100 text-gray-600')

    @property
    def duracion_dias(self):
        if self.fecha_inicio and self.fecha_fin_prevista:
            return (self.fecha_fin_prevista - self.fecha_inicio).days
        return None

    @property
    def sctr_valido(self):
        asignaciones = self.tecnicos.select_related('tecnico').all()
        if not asignaciones.exists():
            return True
        today = timezone.now().date()
        for asig in asignaciones:
            tiene_sctr = self.documentos.filter(
                tipo=Documento.TIPO_SCTR,
                tecnico=asig.tecnico,
                activo=True,
            ).filter(
                models.Q(fecha_vencimiento__isnull=True) | models.Q(fecha_vencimiento__gte=today)
            ).exists()
            if not tiene_sctr:
                return False
        return True


class ColumnaKanban(TimeStampedModel):
    COLOR_CHOICES = [
        ('gray',   'Gris'),
        ('blue',   'Azul'),
        ('amber',  'Ámbar'),
        ('green',  'Verde'),
        ('red',    'Rojo'),
        ('purple', 'Púrpura'),
        ('indigo', 'Índigo'),
        ('pink',   'Rosa'),
    ]
    COLOR_CSS = {
        'gray':   {'bg': 'bg-gray-100',  'txt': 'text-gray-700',   'dot': 'bg-gray-400',   'bdr': 'border-gray-200'},
        'blue':   {'bg': 'bg-blue-50',   'txt': 'text-blue-700',   'dot': 'bg-blue-500',   'bdr': 'border-blue-200'},
        'amber':  {'bg': 'bg-amber-50',  'txt': 'text-amber-700',  'dot': 'bg-amber-400',  'bdr': 'border-amber-200'},
        'green':  {'bg': 'bg-green-50',  'txt': 'text-green-700',  'dot': 'bg-green-500',  'bdr': 'border-green-200'},
        'red':    {'bg': 'bg-red-50',    'txt': 'text-red-700',    'dot': 'bg-red-500',    'bdr': 'border-red-200'},
        'purple': {'bg': 'bg-purple-50', 'txt': 'text-purple-700', 'dot': 'bg-purple-500', 'bdr': 'border-purple-200'},
        'indigo': {'bg': 'bg-indigo-50', 'txt': 'text-indigo-700', 'dot': 'bg-indigo-500', 'bdr': 'border-indigo-200'},
        'pink':   {'bg': 'bg-pink-50',   'txt': 'text-pink-700',   'dot': 'bg-pink-500',   'bdr': 'border-pink-200'},
    }
    DEFAULTS = [
        ('Pendiente',   'pendiente',   0, 'gray',  False),
        ('En progreso', 'en_progreso', 1, 'blue',  False),
        ('En revisión', 'en_revision', 2, 'amber', False),
        ('Completado',  'completado',  3, 'green', True),
    ]

    proyecto  = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='columnas_kanban')
    nombre    = models.CharField(_('Nombre'), max_length=50)
    slug      = models.CharField(_('Slug'), max_length=50)
    orden     = models.PositiveSmallIntegerField(_('Orden'), default=0)
    color     = models.CharField(_('Color'), max_length=20, choices=COLOR_CHOICES, default='gray')
    es_final  = models.BooleanField(_('Es estado final'), default=False)
    activo    = models.BooleanField(_('Activa'), default=True)

    class Meta:
        verbose_name        = _('Columna Kanban')
        verbose_name_plural = _('Columnas Kanban')
        default_permissions = ()
        ordering            = ['orden']
        unique_together     = [['proyecto', 'slug']]

    def __str__(self):
        return f'{self.nombre} ({self.proyecto.numero})'

    @property
    def css(self):
        return self.COLOR_CSS.get(self.color, self.COLOR_CSS['gray'])

    @classmethod
    def crear_defaults(cls, proyecto):
        for nombre, slug, orden, color, es_final in cls.DEFAULTS:
            cls.objects.get_or_create(
                proyecto=proyecto, slug=slug,
                defaults={'nombre': nombre, 'orden': orden, 'color': color, 'es_final': es_final},
            )


class TecnicoAsignado(models.Model):
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE, related_name='tecnicos',
    )
    tecnico = models.ForeignKey(
        'usuarios.Usuario', on_delete=models.PROTECT,
        related_name='proyectos_asignados', verbose_name=_('Técnico'),
    )

    class Meta:
        verbose_name = _('Técnico asignado')
        verbose_name_plural = _('Técnicos asignados')
        unique_together = [['proyecto', 'tecnico']]
        ordering = ['tecnico__first_name', 'tecnico__last_name']

    def __str__(self):
        return f"{self.tecnico.get_full_name()} → {self.proyecto.numero}"


def _documento_upload(instance, filename):
    safe = os.path.basename(filename)
    numero = instance.proyecto.numero if instance.proyecto_id else 'sin-proyecto'
    tipo = instance.tipo or 'otro'
    return f'proyectos/documentos/{numero}/{tipo}/{safe}'


class Documento(TimeStampedModel):
    TIPO_CONTRATO = 'contrato_firmado'
    TIPO_SCTR = 'sctr'
    TIPO_ADDENDUM = 'addendum'
    TIPO_ACTA = 'acta_entrega'
    TIPO_FACTURA = 'factura'
    TIPO_OTRO = 'otro'

    TIPO_CHOICES = [
        (TIPO_CONTRATO, _('Contrato firmado')),
        (TIPO_SCTR, _('SCTR técnico')),
        (TIPO_ADDENDUM, _('Adenda / Addendum')),
        (TIPO_ACTA, _('Acta de entrega')),
        (TIPO_FACTURA, _('Factura')),
        (TIPO_OTRO, _('Otro')),
    ]

    TIPO_BADGE = {
        TIPO_CONTRATO: 'bg-blue-100 text-blue-700',
        TIPO_SCTR: 'bg-orange-100 text-orange-700',
        TIPO_ADDENDUM: 'bg-yellow-100 text-yellow-700',
        TIPO_ACTA: 'bg-green-100 text-green-700',
        TIPO_FACTURA: 'bg-purple-100 text-purple-700',
        TIPO_OTRO: 'bg-gray-100 text-gray-600',
    }

    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE, related_name='documentos',
    )
    tipo = models.CharField(
        _('Tipo'), max_length=20, choices=TIPO_CHOICES, default=TIPO_OTRO,
    )
    titulo = models.CharField(_('Título'), max_length=200)
    archivo = models.FileField(
        _('Archivo'), upload_to=_documento_upload,
    )
    tecnico = models.ForeignKey(
        'usuarios.Usuario', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='sctr_documentos',
        verbose_name=_('Técnico (SCTR)'),
        help_text=_('Solo para documentos SCTR'),
    )
    fecha_vencimiento = models.DateField(
        _('Fecha de vencimiento'), null=True, blank=True,
        help_text=_('Solo para SCTR. Si vence, bloquea inicio de ejecución'),
    )
    activo = models.BooleanField(_('Activo'), default=True)

    class Meta:
        verbose_name = _('Documento')
        verbose_name_plural = _('Documentos')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_tipo_display()} — {self.titulo}"

    @property
    def esta_vencido(self):
        if self.fecha_vencimiento:
            return self.fecha_vencimiento < timezone.now().date()
        return False

    @property
    def tipo_badge_class(self):
        return self.TIPO_BADGE.get(self.tipo, 'bg-gray-100 text-gray-600')

    @property
    def extension(self):
        _, ext = os.path.splitext(self.archivo.name)
        return ext.lower().lstrip('.') if ext else 'file'

    @property
    def nombre_archivo(self):
        return os.path.basename(self.archivo.name)


# ── Kanban — Actividades ──────────────────────────────────────────────────────

class Actividad(TimeStampedModel):
    ESTADO_PENDIENTE   = 'pendiente'
    ESTADO_EN_PROGRESO = 'en_progreso'
    ESTADO_EN_REVISION = 'en_revision'
    ESTADO_COMPLETADO  = 'completado'
    ESTADO_CANCELADO   = 'cancelado'

    ESTADO_CHOICES = [
        (ESTADO_PENDIENTE,   _('Pendiente')),
        (ESTADO_EN_PROGRESO, _('En progreso')),
        (ESTADO_EN_REVISION, _('En revisión')),
        (ESTADO_COMPLETADO,  _('Completado')),
        (ESTADO_CANCELADO,   _('Cancelado')),
    ]

    COLUMNAS_KANBAN = [
        ESTADO_PENDIENTE, ESTADO_EN_PROGRESO, ESTADO_EN_REVISION, ESTADO_COMPLETADO,
    ]

    PRIORIDAD_BAJA    = 'baja'
    PRIORIDAD_MEDIA   = 'media'
    PRIORIDAD_ALTA    = 'alta'
    PRIORIDAD_CRITICA = 'critica'

    PRIORIDAD_CHOICES = [
        (PRIORIDAD_BAJA,    _('Baja')),
        (PRIORIDAD_MEDIA,   _('Media')),
        (PRIORIDAD_ALTA,    _('Alta')),
        (PRIORIDAD_CRITICA, _('Crítica')),
    ]

    PRIORIDAD_COLOR = {
        PRIORIDAD_BAJA:    'bg-gray-100 text-gray-600',
        PRIORIDAD_MEDIA:   'bg-blue-100 text-blue-700',
        PRIORIDAD_ALTA:    'bg-amber-100 text-amber-700',
        PRIORIDAD_CRITICA: 'bg-red-100 text-red-700',
    }

    PRIORIDAD_BORDER = {
        PRIORIDAD_BAJA:    'border-l-gray-300',
        PRIORIDAD_MEDIA:   'border-l-blue-400',
        PRIORIDAD_ALTA:    'border-l-amber-400',
        PRIORIDAD_CRITICA: 'border-l-red-500',
    }

    proyecto          = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='actividades')
    grupo             = models.CharField(_('Épica / Grupo'), max_length=80, blank=True,
                            help_text=_('Agrupa actividades por épica o sub-fase'))
    titulo            = models.CharField(_('Título'), max_length=200)
    descripcion       = models.TextField(_('Descripción'), blank=True)
    estado            = models.CharField(_('Estado'), max_length=20, choices=ESTADO_CHOICES, default=ESTADO_PENDIENTE)
    prioridad         = models.CharField(_('Prioridad'), max_length=10, choices=PRIORIDAD_CHOICES, default=PRIORIDAD_MEDIA)
    responsable       = models.ForeignKey(
        'usuarios.Usuario', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='actividades_asignadas',
        verbose_name=_('Responsable'),
    )
    fecha_inicio      = models.DateField(_('Fecha inicio'), null=True, blank=True)
    fecha_vencimiento = models.DateField(_('Fecha vencimiento'), null=True, blank=True)
    progreso          = models.PositiveSmallIntegerField(_('Progreso (%)'), default=0)
    orden             = models.PositiveIntegerField(_('Orden'), default=0, db_index=True)
    activo            = models.BooleanField(_('Activa'), default=True)

    class Meta:
        verbose_name = _('Actividad')
        verbose_name_plural = _('Actividades')
        ordering = ['orden', 'created_at']
        default_permissions = ()

    def __str__(self):
        return self.titulo

    @property
    def esta_vencida(self):
        if self.fecha_vencimiento and self.estado not in (self.ESTADO_COMPLETADO, self.ESTADO_CANCELADO):
            return self.fecha_vencimiento < datetime.date.today()
        return False

    @property
    def prioridad_badge(self):
        return self.PRIORIDAD_COLOR.get(self.prioridad, '')

    @property
    def prioridad_border(self):
        return self.PRIORIDAD_BORDER.get(self.prioridad, 'border-l-gray-300')

    @property
    def responsable_iniciales(self):
        if not self.responsable:
            return ''
        r = self.responsable
        fn = r.first_name[:1].upper() if r.first_name else ''
        ln = r.last_name[:1].upper() if r.last_name else ''
        return fn + ln or r.username[:2].upper()

    @property
    def total_horas(self):
        from django.db.models import Sum
        result = self.registros_tiempo.aggregate(total=Sum('horas'))
        return result['total'] or 0


class ComentarioActividad(TimeStampedModel):
    actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE, related_name='comentarios')
    autor     = models.ForeignKey(
        'usuarios.Usuario', on_delete=models.SET_NULL,
        null=True, related_name='+',
    )
    texto = models.TextField(_('Comentario'))

    class Meta:
        verbose_name = _('Comentario')
        ordering = ['created_at']

    def __str__(self):
        return f'Comentario #{self.pk}'


class RegistroTiempo(TimeStampedModel):
    actividad   = models.ForeignKey(
        Actividad, on_delete=models.CASCADE,
        related_name='registros_tiempo', verbose_name=_('Actividad'),
    )
    usuario     = models.ForeignKey(
        'usuarios.Usuario', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='registros_tiempo', verbose_name=_('Usuario'),
    )
    fecha       = models.DateField(_('Fecha'), default=datetime.date.today)
    horas       = models.DecimalField(_('Horas'), max_digits=5, decimal_places=2)
    descripcion = models.TextField(_('Descripción'), blank=True)

    class Meta:
        verbose_name        = _('Registro de tiempo')
        verbose_name_plural = _('Registros de tiempo')
        default_permissions = ()
        ordering            = ['-fecha', '-created_at']

    def __str__(self):
        return f'{self.usuario} – {self.horas}h el {self.fecha}'
