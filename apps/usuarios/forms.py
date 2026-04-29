from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _

from .models import Rol, Usuario

_F = 'w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white'
_FILE = 'w-full text-sm text-gray-600 file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer'


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Usuario',
        widget=forms.TextInput(attrs={'autofocus': True, 'placeholder': 'Ingresa tu usuario'}),
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Ingresa tu contraseña'}),
    )


class RolForm(forms.ModelForm):
    class Meta:
        model = Rol
        fields = ['nombre', 'tipo', 'descripcion', 'color_badge', 'es_superadmin', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': _F, 'placeholder': 'Ej: Técnico Senior, Coordinador'}),
            'tipo': forms.Select(attrs={'class': _F}),
            'descripcion': forms.TextInput(attrs={'class': _F, 'placeholder': 'Descripción corta del rol'}),
            'color_badge': forms.Select(attrs={'class': _F}),
            'es_superadmin': forms.CheckboxInput(attrs={'class': 'h-4 w-4 rounded border-gray-300 text-blue-600'}),
            'activo': forms.CheckboxInput(attrs={'class': 'h-4 w-4 rounded border-gray-300 text-blue-600'}),
        }


class UsuarioAdminForm(forms.ModelForm):
    password1 = forms.CharField(
        label=_('Contraseña'), required=False,
        widget=forms.PasswordInput(attrs={'class': _F, 'placeholder': 'Dejar en blanco para no cambiar'}),
    )
    password2 = forms.CharField(
        label=_('Confirmar contraseña'), required=False,
        widget=forms.PasswordInput(attrs={'class': _F, 'placeholder': 'Repetir contraseña'}),
    )

    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'rol', 'telefono', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': _F}),
            'first_name': forms.TextInput(attrs={'class': _F}),
            'last_name': forms.TextInput(attrs={'class': _F}),
            'email': forms.EmailInput(attrs={'class': _F}),
            'rol': forms.Select(attrs={'class': _F}),
            'telefono': forms.TextInput(attrs={'class': _F, 'placeholder': '+51 999 999 999'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4 rounded border-gray-300 text-blue-600'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['rol'].queryset = Rol.objects.filter(activo=True)
        self.fields['rol'].empty_label = _('— Sin rol asignado —')
        if self.instance.pk:
            self.fields['password1'].help_text = 'Solo completar si desea cambiar la contraseña.'

    def clean(self):
        cd = super().clean()
        p1 = cd.get('password1')
        p2 = cd.get('password2')
        if p1 or p2:
            if p1 != p2:
                raise forms.ValidationError({'password2': 'Las contraseñas no coinciden.'})
            if len(p1) < 8:
                raise forms.ValidationError({'password1': 'Mínimo 8 caracteres.'})
        return cd

    def save(self, commit=True):
        user = super().save(commit=False)
        p1 = self.cleaned_data.get('password1')
        if p1:
            user.set_password(p1)
        elif not user.pk:
            user.set_unusable_password()
        if commit:
            user.save()
        return user


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'telefono', 'foto']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': _F}),
            'last_name': forms.TextInput(attrs={'class': _F}),
            'email': forms.EmailInput(attrs={'class': _F}),
            'telefono': forms.TextInput(attrs={'class': _F, 'placeholder': '+51 999 999 999'}),
            'foto': forms.ClearableFileInput(attrs={'class': _FILE}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True


class CambiarPasswordForm(forms.Form):
    password_actual = forms.CharField(
        label=_('Contraseña actual'),
        widget=forms.PasswordInput(attrs={'class': _F}),
    )
    password_nueva = forms.CharField(
        label=_('Nueva contraseña'),
        widget=forms.PasswordInput(attrs={'class': _F}),
        min_length=8,
    )
    password_confirmar = forms.CharField(
        label=_('Confirmar nueva contraseña'),
        widget=forms.PasswordInput(attrs={'class': _F}),
    )

    def clean(self):
        cd = super().clean()
        if cd.get('password_nueva') != cd.get('password_confirmar'):
            raise forms.ValidationError({'password_confirmar': 'Las contraseñas no coinciden.'})
        return cd
