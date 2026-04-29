import os
import re

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel


# ── Variables disponibles para plantillas ────────────────────────────────────

VARIABLES_DISPONIBLES = [
    ('empresa_nombre',    'Nombre de la empresa (Gibit)'),
    ('empresa_ruc',       'RUC de la empresa'),
    ('empresa_direccion', 'Dirección de la empresa'),
    ('empresa_telefono',  'Teléfono de la empresa'),
    ('empresa_email',     'Email de la empresa'),
    ('empresa_web',       'Web de la empresa'),
    ('cliente_nombre',    'Razón social del cliente'),
    ('cliente_ruc',       'RUC del cliente'),
    ('cliente_contacto',  'Nombre del contacto'),
    ('cliente_cargo',     'Cargo del contacto'),
    ('cliente_direccion', 'Dirección del cliente / sede'),
    ('cliente_telefono',  'Teléfono del contacto'),
    ('cliente_email',     'Email del contacto'),
    ('proyecto_numero',   'Número del proyecto'),
    ('proyecto_titulo',   'Título / alcance del proyecto'),
    ('monto_usd',         'Monto total en USD'),
    ('monto_pen',         'Monto total en soles'),
    ('tc_venta',          'Tipo de cambio'),
    ('fecha_inicio',      'Fecha de inicio del proyecto'),
    ('fecha_fin_prevista','Fecha fin prevista'),
    ('duracion_dias',     'Duración en días'),
    ('tecnico_nombres',   'Lista de técnicos asignados'),
    ('fecha_hoy',         'Fecha de hoy'),
    ('anio_actual',       'Año actual'),
]

TIPO_CHOICES_FLAT = [
    ('contrato_servicios',   'Contrato de servicios'),
    ('contrato_mantenimiento','Contrato de mantenimiento'),
    ('contrato_software',    'Contrato de software'),
    ('contrato_consultoria', 'Contrato de consultoría'),
    ('nda',                  'NDA / Confidencialidad'),
    ('adenda',               'Adenda'),
    ('acta_inicio',          'Acta de inicio'),
    ('acta_entrega',         'Acta de entrega / Conformidad'),
    ('orden_trabajo',        'Orden de trabajo'),
    ('carta_garantia',       'Carta de garantía'),
    ('carta_presentacion',   'Carta de presentación'),
    ('informe_tecnico',      'Informe técnico'),
    ('otro',                 'Otro'),
]

TIPO_GRUPOS = [
    ('Contratos', [
        'contrato_servicios', 'contrato_mantenimiento',
        'contrato_software', 'contrato_consultoria', 'nda', 'adenda',
    ]),
    ('Operacional', [
        'acta_inicio', 'acta_entrega', 'orden_trabajo',
        'carta_garantia', 'informe_tecnico',
    ]),
    ('Comercial', ['carta_presentacion', 'otro']),
]


def sustituir_variables(cuerpo_html: str, variables: dict) -> str:
    for clave, valor in variables.items():
        cuerpo_html = cuerpo_html.replace('{{' + clave + '}}', str(valor or ''))
    return cuerpo_html


def build_variables(proyecto=None, empresa=None, config=None) -> dict:
    from django.utils import timezone as tz
    hoy = tz.now().date()
    vars_ = {
        'fecha_hoy':   hoy.strftime('%d de %B de %Y'),
        'anio_actual': str(hoy.year),
        'empresa_nombre': '', 'empresa_ruc': '', 'empresa_direccion': '',
        'empresa_telefono': '', 'empresa_email': '', 'empresa_web': '',
        'cliente_nombre': '', 'cliente_ruc': '', 'cliente_contacto': '',
        'cliente_cargo': '', 'cliente_direccion': '', 'cliente_telefono': '',
        'cliente_email': '', 'proyecto_numero': '', 'proyecto_titulo': '',
        'monto_usd': '', 'monto_pen': '', 'tc_venta': '',
        'fecha_inicio': '', 'fecha_fin_prevista': '', 'duracion_dias': '',
        'tecnico_nombres': '',
    }

    if config:
        vars_.update({
            'empresa_nombre':    config.nombre_empresa,
            'empresa_ruc':       config.ruc,
            'empresa_direccion': config.direccion,
            'empresa_telefono':  config.telefono,
            'empresa_email':     config.email,
            'empresa_web':       config.web,
        })

    if empresa and not proyecto:
        vars_.update({
            'cliente_nombre':    empresa.razon_social,
            'cliente_ruc':       empresa.ruc,
            'cliente_direccion': getattr(empresa, 'address', '') or '',
        })

    if proyecto:
        if proyecto.empresa:
            vars_.update({
                'cliente_nombre':    proyecto.empresa.razon_social,
                'cliente_ruc':       proyecto.empresa.ruc,
                'cliente_direccion': getattr(proyecto.empresa, 'address', '') or '',
            })
        if proyecto.contacto:
            vars_['cliente_contacto'] = proyecto.contacto.nombre
            vars_['cliente_cargo']    = proyecto.contacto.cargo or ''
            vars_['cliente_telefono'] = getattr(proyecto.contacto, 'whatsapp', '') or ''
            vars_['cliente_email']    = getattr(proyecto.contacto, 'correo', '') or ''
        if proyecto.sede and getattr(proyecto.sede, 'address', None):
            vars_['cliente_direccion'] = proyecto.sede.address
        vars_.update({
            'proyecto_numero':    proyecto.numero,
            'proyecto_titulo':    proyecto.titulo,
            'monto_usd':          str(proyecto.valor_usd),
            'monto_pen':          str(proyecto.valor_pen),
            'tc_venta':           str(proyecto.tc_venta or ''),
            'fecha_inicio':       proyecto.fecha_inicio.strftime('%d/%m/%Y') if proyecto.fecha_inicio else '',
            'fecha_fin_prevista': proyecto.fecha_fin_prevista.strftime('%d/%m/%Y') if proyecto.fecha_fin_prevista else '',
            'duracion_dias':      str(proyecto.duracion_dias or ''),
        })
        tecnicos = proyecto.tecnicos.select_related('tecnico').all()
        vars_['tecnico_nombres'] = ', '.join(a.tecnico.get_full_name() for a in tecnicos)

    return vars_


# ── Modelos ──────────────────────────────────────────────────────────────────

class PlantillaDocumento(TimeStampedModel):
    nombre = models.CharField(_('Nombre'), max_length=150,
        help_text=_('Ej: Contrato CCTV Estándar 2025, Adenda v2'))
    tipo = models.CharField(_('Tipo'), max_length=30,
        choices=TIPO_CHOICES_FLAT, default='otro')
    descripcion = models.CharField(_('Descripción'), max_length=250, blank=True)
    cuerpo_html = models.TextField(
        _('Contenido'),
        help_text=_('Usa {{variable}} para datos automáticos al generar'),
        default='',
    )
    es_predeterminada = models.BooleanField(
        _('Predeterminada para este tipo'), default=False,
    )
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='plantillas_creadas',
    )
    activo = models.BooleanField(_('Activa'), default=True)

    class Meta:
        verbose_name = _('Plantilla de documento')
        verbose_name_plural = _('Plantillas de documentos')
        ordering = ['tipo', 'nombre']
        default_permissions = ()
        permissions = [
            ('ver_documentos',         'Ver documentos generados'),
            ('crear_documento',        'Crear documento'),
            ('editar_documento',       'Editar documento'),
            ('eliminar_documento',     'Archivar documento'),
            ('gestionar_plantillas',   'Gestionar plantillas de documentos'),
            ('gestionar_repositorio',  'Gestionar repositorio de archivos'),
        ]

    def __str__(self):
        return self.nombre

    def get_tipo_label(self):
        return dict(TIPO_CHOICES_FLAT).get(self.tipo, self.tipo)

    def generar_para_proyecto(self, proyecto, usuario=None):
        from apps.core.models import Configuracion
        variables = build_variables(proyecto=proyecto, config=Configuracion.get())
        return DocumentoGenerado.objects.create(
            proyecto=proyecto,
            empresa=proyecto.empresa,
            plantilla_origen=self,
            nombre=f'{self.nombre} — {proyecto.numero}',
            tipo=self.tipo,
            cuerpo_html=sustituir_variables(self.cuerpo_html, variables),
            creado_por=usuario,
        )

    def generar_standalone(self, empresa=None, usuario=None):
        from apps.core.models import Configuracion
        variables = build_variables(empresa=empresa, config=Configuracion.get())
        nombre = self.nombre + (f' — {empresa.razon_social}' if empresa else '')
        return DocumentoGenerado.objects.create(
            empresa=empresa,
            plantilla_origen=self,
            nombre=nombre,
            tipo=self.tipo,
            cuerpo_html=sustituir_variables(self.cuerpo_html, variables),
            creado_por=usuario,
        )


class DocumentoGenerado(TimeStampedModel):
    proyecto = models.ForeignKey(
        'proyectos.Proyecto', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='documentos_generados',
    )
    empresa = models.ForeignKey(
        'clientes.Empresa', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='documentos_generados',
    )
    plantilla_origen = models.ForeignKey(
        PlantillaDocumento, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='documentos_generados',
        verbose_name=_('Plantilla de origen'),
    )
    nombre = models.CharField(_('Nombre del documento'), max_length=200)
    tipo = models.CharField(_('Tipo'), max_length=30,
        choices=TIPO_CHOICES_FLAT, default='otro')
    cuerpo_html = models.TextField(_('Contenido editable'))
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='documentos_generados',
    )
    activo = models.BooleanField(_('Activo'), default=True)

    class Meta:
        verbose_name = _('Documento generado')
        verbose_name_plural = _('Documentos generados')
        ordering = ['-created_at']

    def __str__(self):
        return self.nombre

    def get_tipo_label(self):
        return dict(TIPO_CHOICES_FLAT).get(self.tipo, self.tipo)


# ── Repositorio de archivos ───────────────────────────────────────────────────

class CarpetaRepositorio(TimeStampedModel):
    nombre = models.CharField(_('Nombre'), max_length=100)
    descripcion = models.CharField(_('Descripción'), max_length=250, blank=True)
    carpeta_padre = models.ForeignKey(
        'self', on_delete=models.CASCADE,
        null=True, blank=True, related_name='subcarpetas',
        verbose_name=_('Carpeta padre'),
    )
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='+',
    )
    activo = models.BooleanField(_('Activa'), default=True)

    class Meta:
        verbose_name = _('Carpeta de repositorio')
        verbose_name_plural = _('Carpetas de repositorio')
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def get_ancestors(self):
        ancestors = []
        actual = self.carpeta_padre
        while actual:
            ancestors.insert(0, actual)
            actual = actual.carpeta_padre
        return ancestors

    def get_ruta_display(self):
        partes = [a.nombre for a in self.get_ancestors()] + [self.nombre]
        return ' / '.join(partes)


def _slugify_nombre(nombre):
    nombre = nombre.strip().replace(' ', '_')
    return re.sub(r'[^\w\-.]', '', nombre) or 'carpeta'


def _repositorio_upload(instance, filename):
    safe = os.path.basename(filename)
    if instance.carpeta_id:
        carpeta = instance.carpeta
        partes = [_slugify_nombre(a.nombre) for a in carpeta.get_ancestors()]
        partes.append(_slugify_nombre(carpeta.nombre))
        ruta = '/'.join(partes)
        return f'repositorio/{ruta}/{safe}'
    return f'repositorio/{safe}'


_EXT_ICON = {
    'pdf': 'pdf',
    'doc': 'word', 'docx': 'word',
    'xls': 'excel', 'xlsx': 'excel',
    'png': 'image', 'jpg': 'image', 'jpeg': 'image', 'gif': 'image', 'webp': 'image',
    'zip': 'zip', 'rar': 'zip', '7z': 'zip',
    'mp4': 'video', 'avi': 'video', 'mov': 'video',
}


class ArchivoRepositorio(TimeStampedModel):
    carpeta = models.ForeignKey(
        CarpetaRepositorio, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='archivos',
        verbose_name=_('Carpeta'),
    )
    nombre = models.CharField(_('Nombre'), max_length=200)
    descripcion = models.CharField(_('Descripción'), max_length=250, blank=True)
    archivo = models.FileField(_('Archivo'), upload_to=_repositorio_upload)
    tamano_bytes = models.PositiveIntegerField(_('Tamaño (bytes)'), default=0)
    subido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='+',
    )
    activo = models.BooleanField(_('Activo'), default=True)

    class Meta:
        verbose_name = _('Archivo de repositorio')
        verbose_name_plural = _('Archivos de repositorio')
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    @property
    def extension(self):
        _, ext = os.path.splitext(self.archivo.name)
        return ext.lower().lstrip('.')

    @property
    def tamano_display(self):
        b = self.tamano_bytes
        if b < 1024:
            return f'{b} B'
        if b < 1024 ** 2:
            return f'{b / 1024:.1f} KB'
        return f'{b / 1024 ** 2:.1f} MB'

    @property
    def icono_tipo(self):
        return _EXT_ICON.get(self.extension, 'file')
