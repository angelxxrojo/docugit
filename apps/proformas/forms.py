from django import forms
from django.utils.translation import gettext_lazy as _

from apps.clientes.models import Contacto, Sede
from apps.catalogo.models import CondicionComercial, Producto, Servicio, TipoCambio

from .models import Proforma, ProformaItem, ProformaCondicion

_F = 'w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white'
_T = 'w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none bg-white'


class ProformaForm(forms.ModelForm):
    class Meta:
        model = Proforma
        fields = [
            'empresa', 'contacto', 'sede', 'titulo', 'tecnico',
            'tipo_cambio', 'tc_venta', 'margen_objetivo',
            'fecha_emision', 'validez_dias', 'incluye_igv', 'porcentaje_igv', 'observaciones',
        ]
        widgets = {
            'empresa': forms.Select(attrs={
                'class': _F,
                'hx-get': '/proformas/htmx/contactos/',
                'hx-target': '#contacto-sede-wrapper',
                'hx-trigger': 'change',
                'hx-include': '[name=empresa]',
            }),
            'contacto': forms.Select(attrs={'class': _F}),
            'sede': forms.Select(attrs={'class': _F}),
            'titulo': forms.TextInput(attrs={
                'class': _F,
                'placeholder': _('Ej: Propuesta técnica – Sistema ERP módulo inventarios'),
            }),
            'tipo_cambio': forms.Select(attrs={
                'class': _F,
                'id': 'id_tipo_cambio',
                'onchange': 'autoFillTC(this.value)',
            }),
            'tc_venta': forms.NumberInput(attrs={
                'class': _F, 'step': '0.0001', 'placeholder': '3.7500', 'id': 'id_tc_venta',
            }),
            'fecha_emision': forms.DateInput(attrs={'class': _F, 'type': 'date'}, format='%Y-%m-%d'),
            'validez_dias': forms.NumberInput(attrs={'class': _F, 'min': '1', 'max': '365'}),
            'incluye_igv': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 rounded border-gray-300',
                'onchange': 'toggleIGV(this.checked)',
            }),
            'porcentaje_igv': forms.NumberInput(attrs={
                'class': _F, 'step': '0.01', 'min': '0', 'max': '100', 'id': 'id_porcentaje_igv',
            }),
            'tecnico': forms.Select(attrs={'class': _F}),
            'margen_objetivo': forms.NumberInput(attrs={
                'class': _F, 'step': '0.5', 'min': '0', 'max': '500',
                'placeholder': '0', 'id': 'id_margen_objetivo',
            }),
            'observaciones': forms.Textarea(attrs={
                'class': _T, 'rows': 3,
                'placeholder': _('Notas adicionales para el cliente...'),
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contacto'].required = False
        self.fields['sede'].required = False
        self.fields['tipo_cambio'].required = False
        self.fields['tc_venta'].required = False
        self.fields['observaciones'].required = False
        self.fields['tecnico'].required = False
        self.fields['tecnico'].empty_label = _('— Sin técnico asignado —')
        from django.db.models import Q
        from apps.usuarios.models import Usuario
        tecnico_actual_id = self.instance.tecnico_id if self.instance.pk else None
        self.fields['tecnico'].queryset = (
            Usuario.objects.filter(
                Q(is_active=True) | Q(pk=tecnico_actual_id)
            ).select_related('rol').order_by('first_name', 'last_name').distinct()
        )
        self.fields['fecha_emision'].input_formats = ['%Y-%m-%d']

        vigentes_ids = list(TipoCambio.get_vigentes().values_list('id', flat=True))
        self.fields['tipo_cambio'].queryset = (
            TipoCambio.objects.filter(id__in=vigentes_ids).select_related('moneda')
        )
        self.fields['tipo_cambio'].empty_label = _('Sin tipo de cambio')
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


class ProformaItemForm(forms.ModelForm):
    class Meta:
        model = ProformaItem
        fields = ['servicio', 'producto', 'descripcion', 'descripcion_tecnica', 'unidad', 'cantidad', 'precio_usd', 'costo', 'moneda_costo']
        widgets = {
            'servicio': forms.Select(attrs={
                'class': _F, 'id': 'item_servicio',
                'onchange': 'autoFillServicio(this.value)',
            }),
            'producto': forms.Select(attrs={
                'class': _F, 'id': 'item_producto',
                'onchange': 'autoFillProducto(this.value)',
            }),
            'descripcion': forms.TextInput(attrs={
                'class': _F, 'placeholder': _('Nombre del servicio o ítem'),
                'id': 'item_descripcion',
            }),
            'descripcion_tecnica': forms.Textarea(attrs={
                'class': _T, 'rows': 2,
                'placeholder': _('Alcance técnico (opcional)'),
                'id': 'item_descripcion_tecnica',
            }),
            'unidad': forms.Select(attrs={'class': _F, 'id': 'item_unidad'}),
            'cantidad': forms.NumberInput(attrs={
                'class': _F, 'step': '0.01', 'min': '0.01', 'id': 'item_cantidad',
            }),
            'precio_usd': forms.NumberInput(attrs={
                'class': _F, 'step': '0.01', 'min': '0', 'placeholder': '0.00',
                'id': 'item_precio_usd',
                'oninput': 'recalcMargenActual()',
            }),
            'costo': forms.NumberInput(attrs={
                'class': _F, 'step': '0.01', 'min': '0', 'placeholder': '0.00',
                'id': 'item_costo',
                'oninput': 'recalcSugerido()',
            }),
            'moneda_costo': forms.Select(attrs={
                'class': _F, 'id': 'item_moneda_costo',
                'onchange': 'recalcSugerido()',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['servicio'].required = False
        self.fields['servicio'].empty_label = _('— Seleccionar servicio')
        self.fields['servicio'].queryset = (
            Servicio.objects.filter(activo=True)
            .select_related('categoria')
            .order_by('categoria__nombre', 'nombre')
        )
        self.fields['producto'].required = False
        self.fields['producto'].empty_label = _('— Seleccionar producto')
        self.fields['producto'].queryset = (
            Producto.objects.filter(activo=True)
            .select_related('categoria')
            .order_by('categoria__nombre', 'nombre')
        )
        self.fields['descripcion_tecnica'].required = False
        self.fields['costo'].required = False
        self.fields['moneda_costo'].required = False


class ProformaCondicionForm(forms.ModelForm):
    class Meta:
        model = ProformaCondicion
        fields = ['condicion_ref', 'titulo', 'contenido']
        widgets = {
            'condicion_ref': forms.Select(attrs={
                'class': _F, 'id': 'cond_ref',
                'onchange': 'autoFillCondicion(this.value)',
            }),
            'titulo': forms.TextInput(attrs={
                'class': _F, 'placeholder': _('Ej: Condiciones de pago'),
                'id': 'cond_titulo',
            }),
            'contenido': forms.Textarea(attrs={
                'class': _T, 'rows': 4, 'id': 'cond_contenido',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['condicion_ref'].required = False
        self.fields['condicion_ref'].empty_label = _('— Condición personalizada')
        self.fields['condicion_ref'].queryset = (
            CondicionComercial.objects.filter(activo=True).order_by('tipo', 'nombre')
        )
