from django import forms
from django.utils.translation import gettext_lazy as _

from .models import (
    CategoriaServicio, CategoriaProducto, CondicionComercial,
    CuentaBancaria, Moneda, Producto, Servicio, TipoCambio,
)

INPUT_CLASS = (
    'block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm '
    'text-gray-900 placeholder-gray-400 focus:border-blue-500 focus:outline-none '
    'focus:ring-1 focus:ring-blue-500'
)
SELECT_CLASS = (
    'block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm '
    'text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500'
)
CHECKBOX_CLASS = 'h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500'
TEXTAREA_CLASS = (
    'block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm '
    'text-gray-900 placeholder-gray-400 focus:border-blue-500 focus:outline-none '
    'focus:ring-1 focus:ring-blue-500 resize-y'
)


class CategoriaServicioForm(forms.ModelForm):
    class Meta:
        model = CategoriaServicio
        fields = ['nombre', 'descripcion', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': INPUT_CLASS,
                                             'placeholder': 'Ej: Videovigilancia'}),
            'descripcion': forms.TextInput(attrs={'class': INPUT_CLASS,
                                                  'placeholder': 'Descripción breve (opcional)'}),
            'activo': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}),
        }


class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = ['categoria', 'codigo', 'nombre', 'descripcion', 'unidad', 'precio_usd', 'costo', 'moneda_costo', 'activo']
        widgets = {
            'categoria': forms.Select(attrs={'class': SELECT_CLASS}),
            'codigo': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Ej: CCTV-01'}),
            'nombre': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Nombre del servicio'}),
            'descripcion': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 4,
                                                  'placeholder': 'Descripción técnica detallada…'}),
            'unidad': forms.Select(attrs={'class': SELECT_CLASS}),
            'precio_usd': forms.NumberInput(attrs={'class': INPUT_CLASS, 'step': '0.01', 'min': '0',
                                                    'placeholder': '0.00'}),
            'costo': forms.NumberInput(attrs={'class': INPUT_CLASS, 'step': '0.01', 'min': '0',
                                              'placeholder': '0.00'}),
            'moneda_costo': forms.Select(attrs={'class': SELECT_CLASS}),
            'activo': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['costo'].required = False
        self.fields['moneda_costo'].required = False


class CondicionComercialForm(forms.ModelForm):
    class Meta:
        model = CondicionComercial
        fields = ['nombre', 'tipo', 'contenido', 'es_default', 'orden', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': INPUT_CLASS,
                                             'placeholder': 'Ej: Adelanto 30% al inicio'}),
            'tipo': forms.Select(attrs={'class': SELECT_CLASS}),
            'contenido': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 5,
                                               'placeholder': 'Texto completo de la condición…'}),
            'es_default': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}),
            'orden': forms.NumberInput(attrs={'class': INPUT_CLASS, 'min': '0'}),
            'activo': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}),
        }


class CuentaBancariaForm(forms.ModelForm):
    class Meta:
        model = CuentaBancaria
        fields = ['banco', 'moneda', 'numero_cuenta', 'cci', 'titular',
                  'es_detraccion', 'porcentaje_detraccion', 'activo']
        widgets = {
            'banco': forms.Select(attrs={'class': SELECT_CLASS}),
            'moneda': forms.Select(attrs={'class': SELECT_CLASS}),
            'numero_cuenta': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': '000-000000000-0-00'}),
            'cci': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': '00200000000000000000 (opcional)'}),
            'titular': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Gibit Tecnología S.A.C.'}),
            'es_detraccion': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}),
            'porcentaje_detraccion': forms.NumberInput(attrs={'class': INPUT_CLASS, 'step': '0.01',
                                                               'min': '0', 'max': '100',
                                                               'placeholder': 'Ej: 4.00'}),
            'activo': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}),
        }


class MonedaForm(forms.ModelForm):
    class Meta:
        model = Moneda
        fields = ['codigo', 'nombre', 'simbolo', 'activo']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': INPUT_CLASS,
                                             'placeholder': 'Ej: USD, EUR, GBP',
                                             'style': 'text-transform:uppercase'}),
            'nombre': forms.TextInput(attrs={'class': INPUT_CLASS,
                                             'placeholder': 'Ej: Dólar americano'}),
            'simbolo': forms.TextInput(attrs={'class': INPUT_CLASS,
                                              'placeholder': 'Ej: $, €, £'}),
            'activo': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}),
        }

    def clean_codigo(self):
        return self.cleaned_data.get('codigo', '').strip().upper()


class CategoriaProductoForm(forms.ModelForm):
    class Meta:
        model = CategoriaProducto
        fields = ['nombre', 'descripcion', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': INPUT_CLASS,
                                             'placeholder': 'Ej: Cámaras CCTV, Grabadores DVR, Redes'}),
            'descripcion': forms.TextInput(attrs={'class': INPUT_CLASS,
                                                  'placeholder': 'Descripción breve (opcional)'}),
            'activo': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}),
        }


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['categoria', 'nombre', 'marca', 'modelo', 'descripcion', 'unidad', 'precio_usd', 'moneda_costo', 'activo']
        widgets = {
            'categoria': forms.Select(attrs={'class': SELECT_CLASS}),
            'nombre': forms.TextInput(attrs={'class': INPUT_CLASS,
                                             'placeholder': 'Ej: Cámara TURRET 5MP ColorVu SmartHybrid'}),
            'marca': forms.TextInput(attrs={'class': INPUT_CLASS,
                                            'placeholder': 'Ej: Hikvision, Dahua, Western Digital'}),
            'modelo': forms.TextInput(attrs={'class': INPUT_CLASS,
                                             'placeholder': 'Ej: DS-2CE70KF0T-LPFS',
                                             'style': 'font-family: monospace'}),
            'descripcion': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 5,
                                                  'placeholder': 'Especificaciones técnicas (una por línea):\n5MP resolución\nVision nocturna 20m\n2.8mm lente fijo'}),
            'unidad': forms.Select(attrs={'class': SELECT_CLASS}),
            'precio_usd': forms.NumberInput(attrs={'class': INPUT_CLASS, 'step': '0.01', 'min': '0',
                                                    'placeholder': '0.00'}),
            'moneda_costo': forms.Select(attrs={'class': SELECT_CLASS}),
            'activo': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['moneda_costo'].required = False


class TipoCambioForm(forms.ModelForm):
    class Meta:
        model = TipoCambio
        fields = ['moneda', 'compra', 'venta', 'nota']
        widgets = {
            'moneda': forms.Select(attrs={'class': SELECT_CLASS}),
            'compra': forms.NumberInput(attrs={'class': INPUT_CLASS, 'step': '0.0001', 'min': '0',
                                               'placeholder': '3.7000'}),
            'venta': forms.NumberInput(attrs={'class': INPUT_CLASS, 'step': '0.0001', 'min': '0',
                                              'placeholder': '3.7200'}),
            'nota': forms.TextInput(attrs={'class': INPUT_CLASS,
                                           'placeholder': 'Ej: Fuente SBS (opcional)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['moneda'].queryset = Moneda.objects.filter(activo=True).order_by('codigo')
