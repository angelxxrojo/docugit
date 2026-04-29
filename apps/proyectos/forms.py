from django import forms
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.clientes.models import Contacto, Sede
from apps.proformas.models import Proforma
from apps.usuarios.models import Usuario

from .models import (Actividad, ComentarioActividad, ColumnaKanban,
                     Documento, Proyecto, RegistroTiempo, TecnicoAsignado)

_F = 'w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white'
_T = 'w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none bg-white'
_FILE = 'w-full text-sm text-gray-600 file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer'


class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = [
            'proforma',
            'empresa', 'contacto', 'sede', 'titulo',
            'fecha_inicio', 'fecha_fin_prevista',
            'valor_usd', 'tc_venta', 'valor_pen',
            'observaciones', 'texto_contrato',
        ]
        widgets = {
            'proforma': forms.Select(attrs={
                'class': _F,
                'id': 'id_proforma',
                'onchange': 'autoFillDesdeProforma(this.value)',
            }),
            'empresa': forms.Select(attrs={
                'class': _F,
                'hx-get': '/proyectos/htmx/contactos/',
                'hx-target': '#contacto-sede-wrapper',
                'hx-trigger': 'change',
                'hx-include': '[name=empresa]',
            }),
            'contacto': forms.Select(attrs={'class': _F}),
            'sede': forms.Select(attrs={'class': _F}),
            'titulo': forms.TextInput(attrs={
                'class': _F,
                'placeholder': _('Ej: Instalación sistema CCTV 16 cámaras – Sede Miraflores'),
            }),
            'fecha_inicio': forms.DateInput(format='%Y-%m-%d', attrs={'class': _F, 'type': 'date'}),
            'fecha_fin_prevista': forms.DateInput(format='%Y-%m-%d', attrs={'class': _F, 'type': 'date'}),
            'valor_usd': forms.NumberInput(attrs={
                'class': _F, 'step': '0.01', 'min': '0', 'id': 'id_valor_usd',
            }),
            'tc_venta': forms.NumberInput(attrs={
                'class': _F, 'step': '0.0001', 'placeholder': '3.7500',
                'id': 'id_tc_venta',
                'onchange': 'recalcularPen()',
            }),
            'valor_pen': forms.NumberInput(attrs={
                'class': _F, 'step': '0.01', 'min': '0', 'id': 'id_valor_pen',
            }),
            'observaciones': forms.Textarea(attrs={
                'class': _T, 'rows': 3,
                'placeholder': _('Notas internas del proyecto...'),
            }),
            'texto_contrato': forms.Textarea(attrs={
                'class': _T, 'rows': 6,
                'placeholder': _('Cláusulas del contrato: alcance, entregables, condiciones de pago, garantía...'),
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['proforma'].required = False
        self.fields['proforma'].empty_label = _('Sin proforma de origen')
        self.fields['proforma'].queryset = (
            Proforma.objects.filter(activo=True, es_vigente=True)
            .select_related('empresa')
            .order_by('-created_at')
        )
        self.fields['contacto'].required = False
        self.fields['sede'].required = False
        self.fields['tc_venta'].required = False
        self.fields['valor_pen'].required = False
        self.fields['observaciones'].required = False
        self.fields['texto_contrato'].required = False
        self.fields['fecha_inicio'].required = False
        self.fields['fecha_fin_prevista'].required = False
        self.fields['contacto'].empty_label = _('Sin contacto asignado')
        self.fields['sede'].empty_label = _('Sin sede específica')

        empresa_id = None
        if self.instance.pk:
            empresa_id = self.instance.empresa_id
        elif self.data.get('empresa'):
            try:
                empresa_id = int(self.data['empresa'])
            except (ValueError, TypeError):
                pass

        if empresa_id:
            self.fields['contacto'].queryset = Contacto.objects.filter(
                empresa_id=empresa_id, activo=True,
            ).order_by('-es_principal', 'nombre')
            self.fields['sede'].queryset = Sede.objects.filter(
                empresa_id=empresa_id, activo=True,
            ).order_by('-es_principal', 'nombre')
        else:
            self.fields['contacto'].queryset = Contacto.objects.none()
            self.fields['sede'].queryset = Sede.objects.none()


class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['tipo', 'titulo', 'archivo', 'tecnico', 'fecha_vencimiento']
        widgets = {
            'tipo': forms.Select(attrs={'class': _F, 'id': 'doc_tipo', 'onchange': 'toggleSctrFields(this.value)'}),
            'titulo': forms.TextInput(attrs={
                'class': _F, 'placeholder': _('Ej: Contrato firmado cliente, SCTR Juan Pérez'),
            }),
            'archivo': forms.ClearableFileInput(attrs={'class': _FILE}),
            'tecnico': forms.Select(attrs={'class': _F, 'id': 'doc_tecnico'}),
            'fecha_vencimiento': forms.DateInput(format='%Y-%m-%d', attrs={
                'class': _F, 'type': 'date', 'id': 'doc_fecha_vencimiento',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tecnico'].required = False
        self.fields['fecha_vencimiento'].required = False
        self.fields['tecnico'].empty_label = _('— Seleccionar técnico')
        self.fields['tecnico'].queryset = (
            Usuario.objects.filter(rol__tipo='tecnico', is_active=True)
            .order_by('first_name', 'last_name')
        )


class TecnicoAsignadoForm(forms.ModelForm):
    class Meta:
        model = TecnicoAsignado
        fields = ['tecnico']
        widgets = {
            'tecnico': forms.Select(attrs={'class': _F}),
        }

    def __init__(self, *args, proyecto=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tecnico'].empty_label = _('— Seleccionar técnico')
        qs = Usuario.objects.filter(rol__tipo='tecnico', is_active=True).order_by('first_name', 'last_name')
        if proyecto:
            ya_asignados = proyecto.tecnicos.values_list('tecnico_id', flat=True)
            qs = qs.exclude(pk__in=ya_asignados)
        self.fields['tecnico'].queryset = qs


class ActividadForm(forms.ModelForm):
    class Meta:
        model = Actividad
        fields = ['titulo', 'grupo', 'descripcion', 'estado', 'prioridad', 'responsable',
                  'fecha_inicio', 'fecha_vencimiento', 'progreso']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': _F, 'placeholder': _('Título de la actividad'),
            }),
            'grupo': forms.TextInput(attrs={
                'class': _F, 'placeholder': _('Épica / sub-fase (opcional)'),
                'list': 'grupos-datalist',
            }),
            'descripcion': forms.Textarea(attrs={
                'class': _T, 'rows': 3, 'placeholder': _('Descripción detallada (opcional)'),
            }),
            'estado': forms.Select(attrs={'class': _F}),
            'prioridad': forms.Select(attrs={'class': _F}),
            'responsable': forms.Select(attrs={'class': _F}),
            'fecha_inicio': forms.DateInput(format='%Y-%m-%d', attrs={'class': _F, 'type': 'date'}),
            'fecha_vencimiento': forms.DateInput(format='%Y-%m-%d', attrs={'class': _F, 'type': 'date'}),
            'progreso': forms.NumberInput(attrs={'class': _F, 'min': '0', 'max': '100', 'step': '5'}),
        }

    def __init__(self, *args, proyecto=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['grupo'].required = False
        self.fields['descripcion'].required = False
        self.fields['responsable'].required = False
        self.fields['fecha_inicio'].required = False
        self.fields['fecha_vencimiento'].required = False
        self.fields['responsable'].empty_label = _('— Sin responsable')
        self._proyecto = proyecto
        # Estado: choices dinámicos desde las columnas del proyecto
        if proyecto:
            columnas = proyecto.columnas_kanban.filter(activo=True).order_by('orden')
            self.fields['estado'].choices = [(c.slug, c.nombre) for c in columnas]
        # Responsable: técnicos del proyecto + admins/supervisores
        qs = Usuario.objects.filter(is_active=True).order_by('first_name', 'last_name')
        if proyecto:
            tecnicos_ids = proyecto.tecnicos.values_list('tecnico_id', flat=True)
            qs = Usuario.objects.filter(
                is_active=True
            ).filter(
                models.Q(pk__in=tecnicos_ids) | models.Q(rol__tipo__in=['admin', 'supervisor'])
            ).distinct().order_by('first_name', 'last_name')
        self.fields['responsable'].queryset = qs

    @property
    def grupos_existentes(self):
        if self._proyecto:
            return list(
                self._proyecto.actividades.filter(activo=True)
                .exclude(grupo='')
                .values_list('grupo', flat=True)
                .distinct()
                .order_by('grupo')
            )
        return []


class ActividadQuickForm(forms.Form):
    titulo = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': _F,
            'placeholder': _('Título de la actividad…'),
            'autofocus': True,
        })
    )
    estado = forms.CharField(widget=forms.HiddenInput())


class ComentarioActividadForm(forms.ModelForm):
    class Meta:
        model = ComentarioActividad
        fields = ['texto']
        widgets = {
            'texto': forms.Textarea(attrs={
                'class': _T, 'rows': 2,
                'placeholder': _('Escribe un comentario…'),
            }),
        }


class ColumnaKanbanForm(forms.ModelForm):
    class Meta:
        model = ColumnaKanban
        fields = ['nombre', 'color', 'es_final']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': _F, 'placeholder': _('Ej: Bloqueado, Testing, QA…'),
            }),
            'color': forms.Select(attrs={'class': _F}),
            'es_final': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-blue-600 rounded'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['es_final'].required = False
        self.fields['es_final'].label = _('Marcar como estado final (completado)')


class RegistroTiempoForm(forms.ModelForm):
    class Meta:
        model = RegistroTiempo
        fields = ['fecha', 'horas', 'descripcion']
        widgets = {
            'fecha': forms.DateInput(format='%Y-%m-%d', attrs={'class': _F, 'type': 'date'}),
            'horas': forms.NumberInput(attrs={
                'class': _F, 'min': '0.25', 'max': '24', 'step': '0.25',
                'placeholder': '1.5',
            }),
            'descripcion': forms.Textarea(attrs={
                'class': _T, 'rows': 2,
                'placeholder': _('Qué se trabajó (opcional)…'),
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['descripcion'].required = False
