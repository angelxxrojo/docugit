from django import forms

from .models import ArchivoRepositorio, CarpetaRepositorio, DocumentoGenerado, PlantillaDocumento


class PlantillaForm(forms.ModelForm):
    class Meta:
        model = PlantillaDocumento
        fields = ['nombre', 'tipo', 'descripcion', 'cuerpo_html', 'es_predeterminada']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500',
            }),
            'tipo': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500',
            }),
            'descripcion': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Descripción breve (opcional)',
            }),
            'cuerpo_html': forms.Textarea(attrs={'class': 'w-full'}),
            'es_predeterminada': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 rounded border-gray-300',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cuerpo_html'].required = False


class DocumentoGeneradoForm(forms.ModelForm):
    class Meta:
        model = DocumentoGenerado
        fields = ['nombre', 'tipo', 'cuerpo_html']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500',
            }),
            'tipo': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500',
            }),
            'cuerpo_html': forms.Textarea(attrs={'class': 'w-full'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cuerpo_html'].required = False


_F = 'w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500'
_FILE = 'w-full text-sm text-gray-600 file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer'


class CarpetaRepositorioForm(forms.ModelForm):
    class Meta:
        model = CarpetaRepositorio
        fields = ['nombre', 'descripcion', 'carpeta_padre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': _F, 'placeholder': 'Nombre de la carpeta'}),
            'descripcion': forms.TextInput(attrs={'class': _F, 'placeholder': 'Descripción (opcional)'}),
            'carpeta_padre': forms.Select(attrs={'class': _F}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['descripcion'].required = False
        self.fields['carpeta_padre'].required = False
        self.fields['carpeta_padre'].empty_label = '— Raíz (sin carpeta padre)'
        self.fields['carpeta_padre'].queryset = CarpetaRepositorio.objects.filter(activo=True).order_by('nombre')


class ArchivoRepositorioForm(forms.ModelForm):
    class Meta:
        model = ArchivoRepositorio
        fields = ['nombre', 'descripcion', 'carpeta', 'archivo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': _F, 'placeholder': 'Nombre descriptivo del archivo'}),
            'descripcion': forms.TextInput(attrs={'class': _F, 'placeholder': 'Descripción (opcional)'}),
            'carpeta': forms.Select(attrs={'class': _F}),
            'archivo': forms.ClearableFileInput(attrs={'class': _FILE}),
        }

    def __init__(self, *args, carpeta_inicial=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nombre'].required = False
        self.fields['descripcion'].required = False
        self.fields['carpeta'].required = False
        self.fields['carpeta'].empty_label = '— Raíz (sin carpeta)'
        self.fields['carpeta'].queryset = CarpetaRepositorio.objects.filter(activo=True).order_by('nombre')
        if carpeta_inicial:
            self.fields['carpeta'].initial = carpeta_inicial
