from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, FormView, ListView, TemplateView, UpdateView, View

from apps.clientes.models import Contacto, Empresa

from .forms import CambiarPasswordForm, LoginForm, PerfilForm, RolForm, UsuarioAdminForm
from .models import Rol, Usuario


# ── Auth ─────────────────────────────────────────────────────────────────────

class LoginView(FormView):
    template_name = 'usuarios/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('usuarios:dashboard')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super().form_valid(form)


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('usuarios:login')


# ── Dashboard ─────────────────────────────────────────────────────────────────

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'usuarios/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['total_empresas'] = Empresa.objects.filter(activo=True).count()
        ctx['total_contactos'] = Contacto.objects.count()
        ctx['empresas_recientes'] = (
            Empresa.objects.filter(activo=True).order_by('-created_at')[:5]
        )
        return ctx


# ── Perfil del usuario logueado ───────────────────────────────────────────────

class PerfilView(LoginRequiredMixin, View):
    template_name = 'usuarios/perfil.html'

    def get(self, request):
        from django.shortcuts import render
        form = PerfilForm(instance=request.user)
        pwd_form = CambiarPasswordForm()
        return render(request, self.template_name, {'form': form, 'pwd_form': pwd_form})

    def post(self, request):
        from django.shortcuts import render
        action = request.POST.get('_action', 'perfil')

        if action == 'password':
            pwd_form = CambiarPasswordForm(request.POST)
            form = PerfilForm(instance=request.user)
            if pwd_form.is_valid():
                if not request.user.check_password(pwd_form.cleaned_data['password_actual']):
                    pwd_form.add_error('password_actual', 'Contraseña incorrecta.')
                else:
                    request.user.set_password(pwd_form.cleaned_data['password_nueva'])
                    request.user.save()
                    update_session_auth_hash(request, request.user)
                    messages.success(request, 'Contraseña actualizada correctamente.')
                    return redirect('usuarios:perfil')
        else:
            form = PerfilForm(request.POST, request.FILES, instance=request.user)
            pwd_form = CambiarPasswordForm()
            if form.is_valid():
                form.save()
                messages.success(request, 'Perfil actualizado.')
                return redirect('usuarios:perfil')

        return render(request, self.template_name, {'form': form, 'pwd_form': pwd_form})


# ── CRUD Usuarios ─────────────────────────────────────────────────────────────

class UsuarioListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'usuarios.ver_usuarios'
    model = Usuario
    template_name = 'usuarios/usuario_list.html'
    context_object_name = 'usuarios'

    def get_queryset(self):
        return Usuario.objects.select_related('rol').order_by('first_name', 'last_name')


class UsuarioCreateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'usuarios.gestionar_usuarios'
    template_name = 'usuarios/usuario_form.html'

    def get(self, request):
        from django.shortcuts import render
        return render(request, self.template_name, {
            'form': UsuarioAdminForm(),
            'titulo_pagina': 'Nuevo Usuario',
            'accion': 'Crear usuario',
        })

    def post(self, request):
        from django.shortcuts import render
        form = UsuarioAdminForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Usuario {user.get_full_name() or user.username} creado.')
            return redirect('usuarios:usuario_list')
        return render(request, self.template_name, {
            'form': form,
            'titulo_pagina': 'Nuevo Usuario',
            'accion': 'Crear usuario',
        })


class UsuarioUpdateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'usuarios.gestionar_usuarios'
    template_name = 'usuarios/usuario_form.html'

    def get_object(self, pk):
        from django.shortcuts import get_object_or_404
        return get_object_or_404(Usuario, pk=pk)

    def get(self, request, pk):
        from django.shortcuts import render
        user = self.get_object(pk)
        return render(request, self.template_name, {
            'form': UsuarioAdminForm(instance=user),
            'object': user,
            'titulo_pagina': f'Editar {user.get_full_name() or user.username}',
            'accion': 'Guardar cambios',
        })

    def post(self, request, pk):
        from django.shortcuts import render
        user = self.get_object(pk)
        form = UsuarioAdminForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario actualizado.')
            return redirect('usuarios:usuario_list')
        return render(request, self.template_name, {
            'form': form,
            'object': user,
            'titulo_pagina': f'Editar {user.get_full_name() or user.username}',
            'accion': 'Guardar cambios',
        })


class UsuarioToggleView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'usuarios.gestionar_usuarios'
    def post(self, request, pk):
        from django.shortcuts import get_object_or_404
        user = get_object_or_404(Usuario, pk=pk)
        if user == request.user:
            messages.error(request, 'No puedes desactivar tu propia cuenta.')
        else:
            user.is_active = not user.is_active
            user.save(update_fields=['is_active'])
            estado = 'activado' if user.is_active else 'desactivado'
            messages.success(request, f'Usuario {estado}.')
        return redirect('usuarios:usuario_list')


# ── CRUD Roles ────────────────────────────────────────────────────────────────

class RolListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'usuarios.gestionar_roles'
    model = Rol
    template_name = 'usuarios/rol_list.html'
    context_object_name = 'roles'
    queryset = Rol.objects.prefetch_related('permisos').order_by('nombre')


class RolCreateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'usuarios.gestionar_roles'
    template_name = 'usuarios/rol_form.html'

    _OUR_APPS = ['clientes', 'catalogo', 'proformas', 'proyectos', 'documentos', 'usuarios', 'core']
    _APP_LABELS = {
        'clientes':   'Clientes / CRM',
        'catalogo':   'Catálogo',
        'proformas':  'Proformas',
        'proyectos':  'Proyectos',
        'documentos': 'Documentos',
        'usuarios':   'Usuarios',
        'core':       'Configuración',
    }

    def _get_permisos_grouped(self, rol=None, selected_ids=None):
        from django.contrib.auth.models import Permission
        perms = (
            Permission.objects
            .filter(content_type__app_label__in=self._OUR_APPS)
            .exclude(codename__regex=r'^(add|change|delete|view)_')
            .select_related('content_type')
            .order_by('content_type__app_label', 'codename')
        )
        if selected_ids is not None:
            active_ids = set(selected_ids)
        elif rol:
            active_ids = set(rol.permisos.values_list('id', flat=True))
        else:
            active_ids = set()

        grouped = {}
        for perm in perms:
            app = perm.content_type.app_label
            if app not in grouped:
                grouped[app] = {
                    'label': self._APP_LABELS.get(app, app.capitalize()),
                    'permisos': [],
                }
            grouped[app]['permisos'].append({
                'id': perm.id,
                'codename': perm.codename,
                'nombre': perm.name,
                'checked': perm.id in active_ids,
            })
        return [{'app': k, **v} for k, v in grouped.items()]

    def _save_permisos(self, rol, post_data):
        from django.contrib.auth.models import Permission
        perm_ids = [int(x) for x in post_data.getlist('permisos') if x.isdigit()]
        rol.permisos.set(Permission.objects.filter(id__in=perm_ids))

    def get(self, request):
        from django.shortcuts import render
        return render(request, self.template_name, {
            'form': RolForm(),
            'permisos_grouped': self._get_permisos_grouped(),
            'titulo_pagina': 'Nuevo Rol',
            'accion': 'Crear rol',
        })

    def post(self, request):
        from django.shortcuts import render
        form = RolForm(request.POST)
        if form.is_valid():
            rol = form.save()
            self._save_permisos(rol, request.POST)
            messages.success(request, f'Rol "{rol.nombre}" creado.')
            return redirect('usuarios:rol_list')
        selected_ids = [int(x) for x in request.POST.getlist('permisos') if x.isdigit()]
        return render(request, self.template_name, {
            'form': form,
            'permisos_grouped': self._get_permisos_grouped(selected_ids=selected_ids),
            'titulo_pagina': 'Nuevo Rol',
            'accion': 'Crear rol',
        })


class RolUpdateView(RolCreateView):
    def get_object(self, pk):
        from django.shortcuts import get_object_or_404
        return get_object_or_404(Rol, pk=pk)

    def get(self, request, pk=None):
        from django.shortcuts import render
        rol = self.get_object(pk)
        return render(request, self.template_name, {
            'form': RolForm(instance=rol),
            'object': rol,
            'permisos_grouped': self._get_permisos_grouped(rol),
            'titulo_pagina': f'Editar rol: {rol.nombre}',
            'accion': 'Guardar cambios',
        })

    def post(self, request, pk=None):
        from django.shortcuts import render
        rol = self.get_object(pk)
        form = RolForm(request.POST, instance=rol)
        if form.is_valid():
            rol = form.save()
            self._save_permisos(rol, request.POST)
            messages.success(request, f'Rol "{rol.nombre}" actualizado.')
            return redirect('usuarios:rol_list')
        selected_ids = [int(x) for x in request.POST.getlist('permisos') if x.isdigit()]
        return render(request, self.template_name, {
            'form': form,
            'object': rol,
            'permisos_grouped': self._get_permisos_grouped(rol, selected_ids=selected_ids),
            'titulo_pagina': f'Editar rol: {rol.nombre}',
            'accion': 'Guardar cambios',
        })
