from django import forms
from django.utils.translation import gettext_lazy as _

from apps.location.models import Department, District, Province

from .models import Contacto, Empresa, Sede

INPUT_CLASS = (
    'block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm '
    'text-gray-900 placeholder-gray-400 focus:border-blue-500 focus:outline-none '
    'focus:ring-1 focus:ring-blue-500'
)
CHECKBOX_CLASS = 'h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500'
SELECT_CLASS = (
    'block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm '
    'text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500'
)


class EmpresaForm(forms.ModelForm):
    department = forms.ModelChoiceField(
        queryset=Department.objects.select_related('country').order_by('name'),
        label=_('Departamento'),
        required=False,
        empty_label='— Selecciona departamento —',
        widget=forms.Select(attrs={'class': SELECT_CLASS, 'id': 'id_department'}),
    )
    province = forms.ModelChoiceField(
        queryset=Province.objects.none(),
        label=_('Provincia'),
        required=False,
        empty_label='— Selecciona provincia —',
        widget=forms.Select(attrs={'class': SELECT_CLASS, 'id': 'id_province'}),
    )
    district = forms.ModelChoiceField(
        queryset=District.objects.none(),
        label=_('Distrito'),
        required=False,
        empty_label='— Selecciona distrito —',
        widget=forms.Select(attrs={'class': SELECT_CLASS, 'id': 'id_district'}),
    )

    class Meta:
        model = Empresa
        fields = ['ruc', 'razon_social', 'nombre_comercial', 'sector',
                  'department', 'province', 'district', 'address', 'code_postal']
        widgets = {
            'ruc': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Ej: 20123456789', 'maxlength': 11}),
            'razon_social': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Razón social completa'}),
            'nombre_comercial': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Nombre comercial (opcional)'}),
            'sector': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Ej: Retail, Industria, Servicios'}),
            'address': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Av. / Jr. / Calle y número'}),
            'code_postal': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Código postal (opcional)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        dept_id = self.data.get('department') or (self.instance.pk and self.instance.department_id)
        prov_id = self.data.get('province') or (self.instance.pk and self.instance.province_id)
        if dept_id:
            self.fields['province'].queryset = Province.objects.filter(
                department_id=dept_id
            ).order_by('name')
        if prov_id:
            self.fields['district'].queryset = District.objects.filter(
                province_id=prov_id
            ).order_by('name')

    def clean_ruc(self):
        ruc = self.cleaned_data.get('ruc', '').strip()
        if not ruc.isdigit():
            raise forms.ValidationError(_('El RUC debe contener solo números.'))
        if len(ruc) != 11:
            raise forms.ValidationError(_('El RUC debe tener exactamente 11 dígitos.'))
        return ruc


class SedeForm(forms.ModelForm):
    department = forms.ModelChoiceField(
        queryset=Department.objects.select_related('country').order_by('name'),
        label=_('Departamento'),
        empty_label='— Selecciona departamento —',
        widget=forms.Select(attrs={'class': SELECT_CLASS, 'id': 'id_department'}),
    )
    province = forms.ModelChoiceField(
        queryset=Province.objects.none(),
        label=_('Provincia'),
        empty_label='— Selecciona provincia —',
        widget=forms.Select(attrs={'class': SELECT_CLASS, 'id': 'id_province'}),
    )
    district = forms.ModelChoiceField(
        queryset=District.objects.none(),
        label=_('Distrito'),
        empty_label='— Selecciona distrito —',
        widget=forms.Select(attrs={'class': SELECT_CLASS, 'id': 'id_district'}),
    )

    class Meta:
        model = Sede
        fields = ['nombre', 'department', 'province', 'district', 'address', 'code_postal', 'referencia', 'es_principal', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Ej: Sede Central, Almacén Norte'}),
            'address': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Av. / Jr. / Calle y número'}),
            'code_postal': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Código postal (opcional)'}),
            'referencia': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 2, 'placeholder': 'Referencia o punto de llegada (opcional)'}),
            'es_principal': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}),
            'activo': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        dept_id = self.data.get('department') or (self.instance.pk and self.instance.department_id)
        prov_id = self.data.get('province') or (self.instance.pk and self.instance.province_id)
        if dept_id:
            self.fields['province'].queryset = Province.objects.filter(
                department_id=dept_id
            ).order_by('name')
        if prov_id:
            self.fields['district'].queryset = District.objects.filter(
                province_id=prov_id
            ).order_by('name')


class ContactoForm(forms.ModelForm):
    class Meta:
        model = Contacto
        fields = ['nombre', 'cargo', 'correo', 'whatsapp', 'es_principal', 'recibe_proforma', 'recibe_informe', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Nombre completo'}),
            'cargo': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Ej: Gerente de TI, Jefe de Compras'}),
            'correo': forms.EmailInput(attrs={'class': INPUT_CLASS, 'placeholder': 'correo@empresa.com'}),
            'whatsapp': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Ej: 999888777'}),
            'es_principal': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}),
            'recibe_proforma': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}),
            'recibe_informe': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}),
            'activo': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}),
        }
