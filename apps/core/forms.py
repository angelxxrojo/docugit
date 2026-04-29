from django import forms

from .models import Configuracion

_F = 'w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white'
_FILE = 'w-full text-sm text-gray-600 file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer'


class ConfiguracionForm(forms.ModelForm):
    class Meta:
        model = Configuracion
        fields = ['nombre_empresa', 'ruc', 'slogan', 'direccion', 'telefono', 'email', 'web', 'logo']
        widgets = {
            'nombre_empresa': forms.TextInput(attrs={'class': _F}),
            'ruc': forms.TextInput(attrs={'class': _F, 'placeholder': '20123456789'}),
            'slogan': forms.TextInput(attrs={'class': _F, 'placeholder': 'Seguridad electrónica · Automatización'}),
            'direccion': forms.TextInput(attrs={'class': _F}),
            'telefono': forms.TextInput(attrs={'class': _F, 'placeholder': '+51 01 234 5678'}),
            'email': forms.EmailInput(attrs={'class': _F}),
            'web': forms.TextInput(attrs={'class': _F, 'placeholder': 'www.gibit.pe'}),
            'logo': forms.ClearableFileInput(attrs={'class': _FILE}),
        }
