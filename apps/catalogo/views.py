from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, ListView, TemplateView, UpdateView,
)

from .forms import (
    CategoriaServicioForm, CategoriaProductoForm, CuentaBancariaForm,
    CondicionComercialForm, MonedaForm, ProductoForm, ServicioForm, TipoCambioForm,
)
from .models import (
    CategoriaServicio, CategoriaProducto, CondicionComercial,
    CuentaBancaria, Moneda, Producto, Servicio, TipoCambio,
)


# ── Hub ──────────────────────────────────────────────────────────────────────

class CatalogoIndexView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = 'catalogo.ver_catalogo'
    template_name = 'catalogo/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['total_categorias'] = CategoriaServicio.objects.count()
        ctx['total_servicios'] = Servicio.objects.filter(activo=True).count()
        ctx['total_productos'] = Producto.objects.filter(activo=True).count()
        ctx['total_condiciones'] = CondicionComercial.objects.filter(activo=True).count()
        ctx['total_cuentas'] = CuentaBancaria.objects.filter(activo=True).count()
        ctx['total_monedas'] = Moneda.objects.filter(activo=True).count()
        ctx['tipo_cambio'] = TipoCambio.get_vigente()
        ctx['tipos_vigentes'] = TipoCambio.get_vigentes()
        return ctx


# ── Categorías de servicio ────────────────────────────────────────────────────

class CategoriaListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'catalogo.ver_catalogo'
    model = CategoriaServicio
    template_name = 'catalogo/categoria_list.html'
    context_object_name = 'categorias'

    def get_queryset(self):
        qs = CategoriaServicio.objects.all()
        if self.request.GET.get('mostrar') != 'todos':
            qs = qs.filter(activo=True)
        q = self.request.GET.get('q', '')
        if q:
            qs = qs.filter(nombre__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '')
        ctx['mostrar'] = self.request.GET.get('mostrar', 'activas')
        return ctx


class CategoriaCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'catalogo.gestionar_categorias'
    model = CategoriaServicio
    form_class = CategoriaServicioForm
    template_name = 'catalogo/categoria_form.html'
    success_url = reverse_lazy('catalogo:categoria_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Nueva categoría'
        ctx['accion'] = 'Guardar categoría'
        return ctx

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Categoría "{self.object.nombre}" creada.')
        return response


class CategoriaUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'catalogo.gestionar_categorias'
    model = CategoriaServicio
    form_class = CategoriaServicioForm
    template_name = 'catalogo/categoria_form.html'
    success_url = reverse_lazy('catalogo:categoria_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Editar categoría'
        ctx['accion'] = 'Guardar cambios'
        return ctx

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Categoría "{self.object.nombre}" actualizada.')
        return response


class CategoriaDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'catalogo.gestionar_categorias'
    model = CategoriaServicio
    template_name = 'catalogo/categoria_confirm_delete.html'
    success_url = reverse_lazy('catalogo:categoria_list')

    def form_valid(self, form):
        self.object.activo = False
        self.object.save()
        messages.success(self.request, f'Categoría "{self.object.nombre}" desactivada.')
        return HttpResponseRedirect(self.get_success_url())


# ── Servicios ────────────────────────────────────────────────────────────────

class ServicioListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'catalogo.ver_catalogo'
    model = Servicio
    template_name = 'catalogo/servicio_list.html'
    context_object_name = 'servicios'
    paginate_by = 25

    def get_queryset(self):
        qs = Servicio.objects.select_related('categoria')
        q = self.request.GET.get('q', '')
        if q:
            qs = qs.filter(Q(nombre__icontains=q) | Q(codigo__icontains=q) |
                           Q(descripcion__icontains=q))
        if self.request.GET.get('mostrar') != 'todos':
            qs = qs.filter(activo=True)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '')
        ctx['mostrar'] = self.request.GET.get('mostrar', 'activos')
        ctx['tipo_cambio'] = TipoCambio.get_vigente()
        return ctx


class ServicioCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'catalogo.gestionar_servicios'
    model = Servicio
    form_class = ServicioForm
    template_name = 'catalogo/servicio_form.html'
    success_url = reverse_lazy('catalogo:servicio_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Nuevo servicio'
        ctx['accion'] = 'Guardar servicio'
        return ctx

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Servicio "{self.object.nombre}" creado correctamente.')
        return response


class ServicioUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'catalogo.gestionar_servicios'
    model = Servicio
    form_class = ServicioForm
    template_name = 'catalogo/servicio_form.html'
    success_url = reverse_lazy('catalogo:servicio_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Editar servicio'
        ctx['accion'] = 'Guardar cambios'
        return ctx

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Servicio "{self.object.nombre}" actualizado.')
        return response


class ServicioDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'catalogo.gestionar_servicios'
    model = Servicio
    template_name = 'catalogo/servicio_confirm_delete.html'
    success_url = reverse_lazy('catalogo:servicio_list')

    def form_valid(self, form):
        self.object.activo = False
        self.object.save()
        messages.success(self.request, f'Servicio "{self.object.nombre}" desactivado.')
        return HttpResponseRedirect(self.get_success_url())


# ── Condiciones comerciales ───────────────────────────────────────────────────

class CondicionListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'catalogo.ver_catalogo'
    model = CondicionComercial
    template_name = 'catalogo/condicion_list.html'
    context_object_name = 'condiciones'

    def get_queryset(self):
        qs = CondicionComercial.objects.all()
        if self.request.GET.get('mostrar') != 'todos':
            qs = qs.filter(activo=True)
        q = self.request.GET.get('q', '')
        if q:
            qs = qs.filter(Q(nombre__icontains=q) | Q(contenido__icontains=q))
        tipo = self.request.GET.get('tipo', '')
        if tipo:
            qs = qs.filter(tipo=tipo)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '')
        ctx['mostrar'] = self.request.GET.get('mostrar', 'activas')
        ctx['tipo_filtro'] = self.request.GET.get('tipo', '')
        ctx['tipo_choices'] = CondicionComercial.TIPO_CHOICES
        return ctx


class CondicionCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'catalogo.gestionar_condiciones'
    model = CondicionComercial
    form_class = CondicionComercialForm
    template_name = 'catalogo/condicion_form.html'
    success_url = reverse_lazy('catalogo:condicion_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Nueva condición comercial'
        ctx['accion'] = 'Guardar condición'
        return ctx

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Condición "{self.object.nombre}" creada.')
        return response


class CondicionUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'catalogo.gestionar_condiciones'
    model = CondicionComercial
    form_class = CondicionComercialForm
    template_name = 'catalogo/condicion_form.html'
    success_url = reverse_lazy('catalogo:condicion_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Editar condición comercial'
        ctx['accion'] = 'Guardar cambios'
        return ctx

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Condición "{self.object.nombre}" actualizada.')
        return response


class CondicionDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'catalogo.gestionar_condiciones'
    model = CondicionComercial
    template_name = 'catalogo/condicion_confirm_delete.html'
    success_url = reverse_lazy('catalogo:condicion_list')

    def form_valid(self, form):
        self.object.activo = False
        self.object.save()
        messages.success(self.request, f'Condición "{self.object.nombre}" desactivada.')
        return HttpResponseRedirect(self.get_success_url())


# ── Cuentas bancarias ─────────────────────────────────────────────────────────

class CuentaListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'catalogo.ver_catalogo'
    model = CuentaBancaria
    template_name = 'catalogo/cuenta_list.html'
    context_object_name = 'cuentas'

    def get_queryset(self):
        qs = CuentaBancaria.objects.all()
        if self.request.GET.get('mostrar') != 'todos':
            qs = qs.filter(activo=True)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['mostrar'] = self.request.GET.get('mostrar', 'activas')
        return ctx


class CuentaCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'catalogo.gestionar_cuentas'
    model = CuentaBancaria
    form_class = CuentaBancariaForm
    template_name = 'catalogo/cuenta_form.html'
    success_url = reverse_lazy('catalogo:cuenta_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Nueva cuenta bancaria'
        ctx['accion'] = 'Guardar cuenta'
        return ctx

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Cuenta {self.object} agregada correctamente.')
        return response


class CuentaUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'catalogo.gestionar_cuentas'
    model = CuentaBancaria
    form_class = CuentaBancariaForm
    template_name = 'catalogo/cuenta_form.html'
    success_url = reverse_lazy('catalogo:cuenta_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Editar cuenta bancaria'
        ctx['accion'] = 'Guardar cambios'
        return ctx

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Cuenta {self.object} actualizada.')
        return response


class CuentaDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'catalogo.gestionar_cuentas'
    model = CuentaBancaria
    template_name = 'catalogo/cuenta_confirm_delete.html'
    success_url = reverse_lazy('catalogo:cuenta_list')

    def form_valid(self, form):
        self.object.activo = False
        self.object.save()
        messages.success(self.request, f'Cuenta {self.object} desactivada.')
        return HttpResponseRedirect(self.get_success_url())


# ── Monedas ───────────────────────────────────────────────────────────────────

class MonedaListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'catalogo.ver_catalogo'
    model = Moneda
    template_name = 'catalogo/moneda_list.html'
    context_object_name = 'monedas'

    def get_queryset(self):
        qs = Moneda.objects.all()
        if self.request.GET.get('mostrar') != 'todos':
            qs = qs.filter(activo=True)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['mostrar'] = self.request.GET.get('mostrar', 'activas')
        ctx['vigentes'] = TipoCambio.get_vigentes()
        return ctx


class MonedaCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'catalogo.gestionar_tipos_cambio'
    model = Moneda
    form_class = MonedaForm
    template_name = 'catalogo/moneda_form.html'
    success_url = reverse_lazy('catalogo:moneda_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Nueva moneda'
        ctx['accion'] = 'Guardar moneda'
        return ctx

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Moneda {self.object.codigo} creada.')
        return response


class MonedaUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'catalogo.gestionar_tipos_cambio'
    model = Moneda
    form_class = MonedaForm
    template_name = 'catalogo/moneda_form.html'
    success_url = reverse_lazy('catalogo:moneda_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = f'Editar moneda: {self.object.codigo}'
        ctx['accion'] = 'Guardar cambios'
        return ctx

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Moneda {self.object.codigo} actualizada.')
        return response


class MonedaDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'catalogo.gestionar_tipos_cambio'
    model = Moneda
    template_name = 'catalogo/moneda_confirm_delete.html'
    success_url = reverse_lazy('catalogo:moneda_list')

    def form_valid(self, form):
        self.object.activo = False
        self.object.save()
        messages.success(self.request, f'Moneda {self.object.codigo} desactivada.')
        return HttpResponseRedirect(self.get_success_url())


# ── Tipo de cambio ────────────────────────────────────────────────────────────

class TipoCambioListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'catalogo.ver_catalogo'
    model = TipoCambio
    template_name = 'catalogo/tipocambio_list.html'
    context_object_name = 'registros'
    paginate_by = 30

    def get_queryset(self):
        qs = TipoCambio.objects.select_related('moneda')
        moneda = self.request.GET.get('moneda', '')
        if moneda:
            qs = qs.filter(moneda__codigo=moneda)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['vigentes'] = TipoCambio.get_vigentes()
        ctx['monedas'] = Moneda.objects.filter(activo=True).order_by('codigo')
        ctx['moneda_filtro'] = self.request.GET.get('moneda', '')
        return ctx


class TipoCambioCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'catalogo.gestionar_tipos_cambio'
    model = TipoCambio
    form_class = TipoCambioForm
    template_name = 'catalogo/tipocambio_form.html'
    success_url = reverse_lazy('catalogo:tipocambio_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Registrar tipo de cambio'
        ctx['accion'] = 'Registrar'
        return ctx

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Tipo de cambio {self.object.moneda.codigo} registrado: '
            f'Compra {self.object.moneda.simbolo}{self.object.compra} / '
            f'Venta {self.object.moneda.simbolo}{self.object.venta}.'
        )
        return response


# ── Categorías de producto ────────────────────────────────────────────────────

class CategoriaProductoListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'catalogo.ver_catalogo'
    model = CategoriaProducto
    template_name = 'catalogo/categoria_producto_list.html'
    context_object_name = 'categorias'

    def get_queryset(self):
        qs = CategoriaProducto.objects.all()
        if self.request.GET.get('mostrar') != 'todos':
            qs = qs.filter(activo=True)
        q = self.request.GET.get('q', '')
        if q:
            qs = qs.filter(nombre__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '')
        ctx['mostrar'] = self.request.GET.get('mostrar', 'activas')
        return ctx


class CategoriaProductoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'catalogo.gestionar_categorias'
    model = CategoriaProducto
    form_class = CategoriaProductoForm
    template_name = 'catalogo/categoria_producto_form.html'
    success_url = reverse_lazy('catalogo:categoria_producto_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Nueva categoría de producto'
        ctx['accion'] = 'Guardar categoría'
        return ctx

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Categoría "{self.object.nombre}" creada.')
        return response


class CategoriaProductoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'catalogo.gestionar_categorias'
    model = CategoriaProducto
    form_class = CategoriaProductoForm
    template_name = 'catalogo/categoria_producto_form.html'
    success_url = reverse_lazy('catalogo:categoria_producto_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Editar categoría de producto'
        ctx['accion'] = 'Guardar cambios'
        return ctx

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Categoría "{self.object.nombre}" actualizada.')
        return response


class CategoriaProductoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'catalogo.gestionar_categorias'
    model = CategoriaProducto
    template_name = 'catalogo/categoria_producto_confirm_delete.html'
    success_url = reverse_lazy('catalogo:categoria_producto_list')

    def form_valid(self, form):
        self.object.activo = False
        self.object.save()
        messages.success(self.request, f'Categoría "{self.object.nombre}" desactivada.')
        return HttpResponseRedirect(self.get_success_url())


# ── Productos ─────────────────────────────────────────────────────────────────

class ProductoListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'catalogo.ver_catalogo'
    model = Producto
    template_name = 'catalogo/producto_list.html'
    context_object_name = 'productos'
    paginate_by = 25

    def get_queryset(self):
        qs = Producto.objects.select_related('categoria')
        q = self.request.GET.get('q', '')
        if q:
            qs = qs.filter(
                Q(nombre__icontains=q) | Q(marca__icontains=q) | Q(modelo__icontains=q)
            )
        cat = self.request.GET.get('categoria', '')
        if cat:
            qs = qs.filter(categoria_id=cat)
        if self.request.GET.get('mostrar') != 'todos':
            qs = qs.filter(activo=True)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '')
        ctx['mostrar'] = self.request.GET.get('mostrar', 'activos')
        ctx['categoria_filtro'] = self.request.GET.get('categoria', '')
        ctx['categorias'] = CategoriaProducto.objects.filter(activo=True)
        ctx['tipo_cambio'] = TipoCambio.get_vigente()
        return ctx


class ProductoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'catalogo.gestionar_productos'
    model = Producto
    form_class = ProductoForm
    template_name = 'catalogo/producto_form.html'
    success_url = reverse_lazy('catalogo:producto_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Nuevo producto'
        ctx['accion'] = 'Guardar producto'
        return ctx

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Producto "{self.object.nombre}" creado.')
        return response


class ProductoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'catalogo.gestionar_productos'
    model = Producto
    form_class = ProductoForm
    template_name = 'catalogo/producto_form.html'
    success_url = reverse_lazy('catalogo:producto_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Editar producto'
        ctx['accion'] = 'Guardar cambios'
        return ctx

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Producto "{self.object.nombre}" actualizado.')
        return response


class ProductoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'catalogo.gestionar_productos'
    model = Producto
    template_name = 'catalogo/producto_confirm_delete.html'
    success_url = reverse_lazy('catalogo:producto_list')

    def form_valid(self, form):
        self.object.activo = False
        self.object.save()
        messages.success(self.request, f'Producto "{self.object.nombre}" desactivado.')
        return HttpResponseRedirect(self.get_success_url())
