from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Count, Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView,
)

from .forms import ContactoForm, EmpresaForm, SedeForm
from .models import Contacto, Empresa, Sede


# ─── Empresa ────────────────────────────────────────────────────────────────

class EmpresaListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'clientes.ver_clientes'
    model = Empresa
    template_name = 'clientes/empresa_list.html'
    context_object_name = 'empresas'
    paginate_by = 20

    def get_queryset(self):
        qs = Empresa.objects.filter(activo=True).annotate(
            num_sedes=Count('sedes', distinct=True),
            num_contactos=Count('contactos', distinct=True),
        )
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(ruc__icontains=q)
                | Q(razon_social__icontains=q)
                | Q(nombre_comercial__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '')
        ctx['total'] = Empresa.objects.filter(activo=True).count()
        return ctx


class EmpresaCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'clientes.crear_cliente'
    model = Empresa
    form_class = EmpresaForm
    template_name = 'clientes/empresa_form.html'
    success_url = reverse_lazy('clientes:empresa_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Nueva Empresa'
        ctx['accion'] = 'Crear empresa'
        return ctx

    def form_valid(self, form):
        messages.success(self.request, f'Empresa "{form.instance.razon_social}" creada correctamente.')
        return super().form_valid(form)


class EmpresaUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'clientes.editar_cliente'
    model = Empresa
    form_class = EmpresaForm
    template_name = 'clientes/empresa_form.html'

    def get_success_url(self):
        return reverse_lazy('clientes:empresa_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = f'Editar: {self.object.razon_social}'
        ctx['accion'] = 'Guardar cambios'
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Empresa actualizada correctamente.')
        return super().form_valid(form)


class EmpresaDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = 'clientes.ver_clientes'
    model = Empresa
    template_name = 'clientes/empresa_detail.html'
    context_object_name = 'empresa'

    def get_queryset(self):
        return Empresa.objects.prefetch_related('sedes', 'contactos')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['sedes'] = self.object.sedes.all().order_by('-activo', '-es_principal', 'nombre')
        ctx['contactos'] = self.object.contactos.all().order_by('-activo', '-es_principal', 'nombre')
        ctx['sedes_activas_count'] = self.object.sedes.filter(activo=True).count()
        ctx['contactos_activos_count'] = self.object.contactos.filter(activo=True).count()
        proformas = self.object.proformas.filter(activo=True, es_vigente=True).order_by('-created_at')
        ctx['proformas_empresa'] = proformas
        ctx['proformas_count'] = proformas.count()
        from apps.proyectos.models import Proyecto
        proyectos = Proyecto.objects.filter(empresa=self.object, activo=True).order_by('-created_at')
        ctx['proyectos_empresa'] = proyectos
        ctx['proyectos_count'] = proyectos.count()
        return ctx


class EmpresaDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'clientes.eliminar_cliente'
    model = Empresa
    template_name = 'clientes/empresa_confirm_delete.html'
    success_url = reverse_lazy('clientes:empresa_list')

    def form_valid(self, form):
        # Soft delete: desactivar en lugar de borrar
        self.object = self.get_object()
        self.object.activo = False
        self.object.save()
        messages.success(self.request, f'Empresa "{self.object.razon_social}" desactivada.')
        return redirect(self.success_url)


# ─── Sede ────────────────────────────────────────────────────────────────────

class SedeCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'clientes.gestionar_contactos'
    model = Sede
    form_class = SedeForm
    template_name = 'clientes/sede_form.html'

    def get_empresa(self):
        return get_object_or_404(Empresa, pk=self.kwargs['empresa_pk'])

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['empresa'] = self.get_empresa()
        ctx['titulo'] = 'Nueva Sede'
        ctx['accion'] = 'Crear sede'
        return ctx

    def form_valid(self, form):
        form.instance.empresa = self.get_empresa()
        messages.success(self.request, f'Sede "{form.instance.nombre}" creada correctamente.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('clientes:empresa_detail', kwargs={'pk': self.kwargs['empresa_pk']})


class SedeUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'clientes.gestionar_contactos'
    model = Sede
    form_class = SedeForm
    template_name = 'clientes/sede_form.html'

    def get_empresa(self):
        return get_object_or_404(Empresa, pk=self.kwargs['empresa_pk'])

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['empresa'] = self.get_empresa()
        ctx['titulo'] = f'Editar sede: {self.object.nombre}'
        ctx['accion'] = 'Guardar cambios'
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Sede actualizada correctamente.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('clientes:empresa_detail', kwargs={'pk': self.kwargs['empresa_pk']})


class SedeDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'clientes.gestionar_contactos'
    model = Sede
    template_name = 'clientes/sede_confirm_delete.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['empresa'] = self.object.empresa
        return ctx

    def form_valid(self, form):
        empresa_pk = self.object.empresa_id
        self.object.activo = False
        self.object.save()
        messages.success(self.request, f'Sede "{self.object.nombre}" desactivada.')
        return HttpResponseRedirect(reverse_lazy('clientes:empresa_detail', kwargs={'pk': empresa_pk}))


# ─── Contacto ────────────────────────────────────────────────────────────────

class ContactoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'clientes.gestionar_contactos'
    model = Contacto
    form_class = ContactoForm
    template_name = 'clientes/contacto_form.html'

    def get_empresa(self):
        return get_object_or_404(Empresa, pk=self.kwargs['empresa_pk'])

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['empresa'] = self.get_empresa()
        ctx['titulo'] = 'Nuevo Contacto'
        ctx['accion'] = 'Crear contacto'
        return ctx

    def form_valid(self, form):
        form.instance.empresa = self.get_empresa()
        messages.success(self.request, f'Contacto "{form.instance.nombre}" creado correctamente.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('clientes:empresa_detail', kwargs={'pk': self.kwargs['empresa_pk']})


class ContactoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'clientes.gestionar_contactos'
    model = Contacto
    form_class = ContactoForm
    template_name = 'clientes/contacto_form.html'

    def get_empresa(self):
        return get_object_or_404(Empresa, pk=self.kwargs['empresa_pk'])

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['empresa'] = self.get_empresa()
        ctx['titulo'] = f'Editar contacto: {self.object.nombre}'
        ctx['accion'] = 'Guardar cambios'
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Contacto actualizado correctamente.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('clientes:empresa_detail', kwargs={'pk': self.kwargs['empresa_pk']})


class ContactoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'clientes.gestionar_contactos'
    model = Contacto
    template_name = 'clientes/contacto_confirm_delete.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['empresa'] = self.object.empresa
        return ctx

    def form_valid(self, form):
        empresa_pk = self.object.empresa_id
        self.object.activo = False
        self.object.save()
        messages.success(self.request, f'Contacto "{self.object.nombre}" desactivado.')
        return HttpResponseRedirect(reverse_lazy('clientes:empresa_detail', kwargs={'pk': empresa_pk}))
