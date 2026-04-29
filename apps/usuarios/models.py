from django.contrib.auth.models import AbstractUser, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel


class Rol(TimeStampedModel):
    TIPO_ADMIN = 'admin'
    TIPO_VENDEDOR = 'vendedor'
    TIPO_TECNICO = 'tecnico'
    TIPO_AUDITOR = 'auditor'
    TIPO_CLIENTE = 'cliente'
    TIPO_CUSTOM = 'custom'

    TIPO_CHOICES = [
        (TIPO_ADMIN, 'Administrador'),
        (TIPO_VENDEDOR, 'Vendedor'),
        (TIPO_TECNICO, 'Técnico'),
        (TIPO_AUDITOR, 'Auditor'),
        (TIPO_CLIENTE, 'Cliente'),
        (TIPO_CUSTOM, 'Personalizado'),
    ]

    COLOR_CHOICES = [
        ('bg-purple-100 text-purple-800', 'Violeta'),
        ('bg-blue-100 text-blue-800', 'Azul'),
        ('bg-green-100 text-green-800', 'Verde'),
        ('bg-yellow-100 text-yellow-800', 'Amarillo'),
        ('bg-red-100 text-red-800', 'Rojo'),
        ('bg-indigo-100 text-indigo-800', 'Índigo'),
        ('bg-pink-100 text-pink-800', 'Rosa'),
        ('bg-orange-100 text-orange-800', 'Naranja'),
        ('bg-gray-100 text-gray-800', 'Gris'),
    ]

    nombre = models.CharField(_('Nombre'), max_length=50, unique=True)
    tipo = models.CharField(
        _('Tipo base'), max_length=20, choices=TIPO_CHOICES, default=TIPO_CUSTOM,
        help_text=_('Tipo de rol para clasificación'),
    )
    descripcion = models.CharField(_('Descripción'), max_length=200, blank=True)
    color_badge = models.CharField(
        _('Color'), max_length=80, default='bg-gray-100 text-gray-800',
        choices=COLOR_CHOICES,
    )
    es_superadmin = models.BooleanField(
        _('Acceso total'), default=False,
        help_text=_('Omite todas las restricciones de permisos'),
    )
    permisos = models.ManyToManyField(
        Permission,
        blank=True,
        related_name='roles',
        verbose_name=_('Permisos'),
    )
    activo = models.BooleanField(_('Activo'), default=True)

    class Meta:
        verbose_name = _('Rol')
        verbose_name_plural = _('Roles')
        ordering = ['nombre']
        default_permissions = ()
        permissions = [
            ('ver_usuarios',       'Ver lista de usuarios'),
            ('gestionar_usuarios', 'Gestionar usuarios'),
            ('gestionar_roles',    'Gestionar roles y permisos'),
        ]

    def __str__(self):
        return self.nombre

    def get_rol_display_badge(self):
        return self.color_badge


class Usuario(AbstractUser):
    rol = models.ForeignKey(
        Rol, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='usuarios', verbose_name=_('Rol'),
    )
    foto = models.ImageField(
        _('Foto de perfil'), upload_to='usuarios/fotos/',
        null=True, blank=True,
    )
    telefono = models.CharField(_('Teléfono'), max_length=20, blank=True)

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def es_admin(self):
        return self.is_superuser or (self.rol is not None and self.rol.es_superadmin)

    def puede_ver_costos(self):
        return self.es_admin() or self.has_perm('proformas.ver_costos')

    def has_perm(self, perm, obj=None):
        if not self.is_active:
            return False
        if self.is_superuser:
            return True
        if self.rol and self.rol.es_superadmin and self.rol.activo:
            return True
        if not self.rol or not self.rol.activo:
            return False
        parts = perm.split('.')
        if len(parts) != 2:
            return False
        app_label, codename = parts
        return self.rol.permisos.filter(
            content_type__app_label=app_label,
            codename=codename,
        ).exists()

    def has_module_perms(self, app_label):
        if not self.is_active:
            return False
        if self.is_superuser:
            return True
        if self.rol and self.rol.es_superadmin and self.rol.activo:
            return True
        if not self.rol or not self.rol.activo:
            return False
        return self.rol.permisos.filter(content_type__app_label=app_label).exists()

    def get_rol_display_badge(self):
        if self.rol:
            return self.rol.color_badge
        return 'bg-gray-100 text-gray-800'

    def get_rol_nombre(self):
        return self.rol.nombre if self.rol else '—'
