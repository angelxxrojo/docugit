import json

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.catalogo.models import CondicionComercial, TipoCambio
from apps.clientes.models import Contacto, Sede

from .forms import ProformaCondicionForm, ProformaForm, ProformaItemForm
from .models import Proforma, ProformaCondicion, ProformaItem


def _items_and_totales_response(proforma, item_form, request):
    proforma.refresh_from_db()
    context = {
        'proforma': proforma,
        'items': proforma.items.select_related('servicio').all(),
        'item_form': item_form,
    }
    html = render_to_string('proformas/partials/items_table.html', context, request=request)
    totales_html = render_to_string(
        'proformas/partials/totales.html',
        {'proforma': proforma, 'is_oob': True},
        request=request,
    )
    return HttpResponse(html + totales_html)


def _condiciones_response(proforma, condicion_form, request):
    context = {
        'proforma': proforma,
        'condiciones': proforma.condiciones.all(),
        'condicion_form': condicion_form,
    }
    html = render_to_string('proformas/partials/condiciones_table.html', context, request=request)
    return HttpResponse(html)


# ── List ─────────────────────────────────────────────────────────────────────

class ProformaListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'proformas.ver_proformas'
    model = Proforma
    template_name = 'proformas/proforma_list.html'
    context_object_name = 'proformas'
    paginate_by = 20

    def get_queryset(self):
        qs = Proforma.objects.filter(activo=True, es_vigente=True).select_related('empresa', 'contacto')
        estado = self.request.GET.get('estado')
        if estado:
            qs = qs.filter(estado=estado)
        q = self.request.GET.get('q', '').strip()
        if q:
            from django.db.models import Q
            qs = qs.filter(
                Q(empresa__razon_social__icontains=q) |
                Q(numero__icontains=q) |
                Q(titulo__icontains=q)
            )
        return qs.order_by('-created_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['estado_choices'] = Proforma.ESTADO_CHOICES
        ctx['estado_filtro'] = self.request.GET.get('estado', '')
        ctx['q'] = self.request.GET.get('q', '')
        base_qs = Proforma.objects.filter(activo=True, es_vigente=True)
        ctx['totals'] = {
            'total': base_qs.count(),
            'borrador': base_qs.filter(estado=Proforma.ESTADO_BORRADOR).count(),
            'enviada': base_qs.filter(estado=Proforma.ESTADO_ENVIADA).count(),
            'aprobada': base_qs.filter(estado=Proforma.ESTADO_APROBADA).count(),
        }
        return ctx


# ── Create / Update ───────────────────────────────────────────────────────────

class ProformaCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'proformas.crear_proforma'
    model = Proforma
    form_class = ProformaForm
    template_name = 'proformas/proforma_form.html'

    def get_initial(self):
        initial = super().get_initial()
        tc = TipoCambio.get_vigente('USD')
        if tc:
            initial['tipo_cambio'] = tc.pk
            initial['tc_venta'] = tc.venta
        empresa_id = self.request.GET.get('empresa')
        if empresa_id:
            initial['empresa'] = empresa_id
        return initial

    def form_valid(self, form):
        proforma = form.save(commit=False)
        proforma.numero = Proforma.generar_numero()
        if proforma.tipo_cambio and not proforma.tc_venta:
            proforma.tc_venta = proforma.tipo_cambio.venta
        proforma.save()
        # Auto-load default conditions
        for i, cond in enumerate(
            CondicionComercial.objects.filter(es_default=True, activo=True).order_by('orden')
        ):
            ProformaCondicion.objects.create(
                proforma=proforma,
                condicion_ref=cond,
                orden=i,
                titulo=cond.nombre,
                contenido=cond.contenido,
            )
        return HttpResponseRedirect(
            reverse('proformas:proforma_detail', kwargs={'pk': proforma.pk})
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo_pagina'] = 'Nueva proforma'
        ctx['accion'] = 'Crear proforma'
        ctx['tc_map'] = json.dumps({
            str(tc.pk): str(tc.venta)
            for tc in TipoCambio.get_vigentes()
        })
        return ctx


class ProformaUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'proformas.editar_proforma'
    model = Proforma
    form_class = ProformaForm
    template_name = 'proformas/proforma_form.html'

    def get_queryset(self):
        return Proforma.objects.filter(activo=True)

    def form_valid(self, form):
        proforma = form.save()
        proforma.recalcular_totales()
        return HttpResponseRedirect(
            reverse('proformas:proforma_detail', kwargs={'pk': proforma.pk})
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo_pagina'] = 'Editar proforma'
        ctx['accion'] = 'Guardar cambios'
        ctx['tc_map'] = json.dumps({
            str(tc.pk): str(tc.venta)
            for tc in TipoCambio.get_vigentes()
        })
        return ctx


# ── Detail ────────────────────────────────────────────────────────────────────

class ProformaDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = 'proformas.ver_proformas'
    model = Proforma
    template_name = 'proformas/proforma_detail.html'
    context_object_name = 'proforma'

    def get_queryset(self):
        return Proforma.objects.filter(activo=True).select_related(
            'empresa', 'contacto', 'sede', 'tipo_cambio__moneda',
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['items'] = self.object.items.select_related('servicio', 'producto').all()
        ctx['condiciones'] = self.object.condiciones.all()
        ctx['item_form'] = ProformaItemForm()
        ctx['condicion_form'] = ProformaCondicionForm()
        ctx['versiones'] = (
            Proforma.objects.filter(numero=self.object.numero, activo=True).order_by('version')
        )
        ctx['cuentas'] = None  # used in PDF only
        return ctx


# ── Delete ────────────────────────────────────────────────────────────────────

class ProformaDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'proformas.eliminar_proforma'
    model = Proforma
    template_name = 'proformas/proforma_confirm_delete.html'
    success_url = reverse_lazy('proformas:proforma_list')

    def form_valid(self, form):
        self.object = self.get_object()
        self.object.activo = False
        self.object.save()
        return HttpResponseRedirect(self.success_url)


# ── Items HTMX ────────────────────────────────────────────────────────────────

class ProformaItemCreateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'proformas.editar_proforma'
    def post(self, request, proforma_pk):
        proforma = get_object_or_404(Proforma, pk=proforma_pk, activo=True)
        form = ProformaItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.proforma = proforma
            last = proforma.items.aggregate(m=Max('orden'))['m'] or 0
            item.orden = last + 1
            item.save()
            proforma.recalcular_totales()
            return _items_and_totales_response(proforma, ProformaItemForm(), request)
        return _items_and_totales_response(proforma, form, request)


class ProformaItemDeleteView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'proformas.editar_proforma'
    def post(self, request, proforma_pk, item_pk):
        proforma = get_object_or_404(Proforma, pk=proforma_pk, activo=True)
        item = get_object_or_404(ProformaItem, pk=item_pk, proforma=proforma)
        item.delete()
        proforma.recalcular_totales()
        return _items_and_totales_response(proforma, ProformaItemForm(), request)


class ProformaItemEditView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'proformas.editar_proforma'
    def _edit_context(self, proforma, item, form):
        return {
            'proforma': proforma,
            'items': proforma.items.select_related('servicio', 'producto').all(),
            'item_form': ProformaItemForm(),
            'edit_item': item,
            'edit_form': form,
        }

    def get(self, request, proforma_pk, item_pk):
        proforma = get_object_or_404(Proforma, pk=proforma_pk, activo=True)
        item = get_object_or_404(ProformaItem, pk=item_pk, proforma=proforma)
        html = render_to_string(
            'proformas/partials/items_table.html',
            self._edit_context(proforma, item, ProformaItemForm(instance=item)),
            request=request,
        )
        return HttpResponse(html)

    def post(self, request, proforma_pk, item_pk):
        proforma = get_object_or_404(Proforma, pk=proforma_pk, activo=True)
        item = get_object_or_404(ProformaItem, pk=item_pk, proforma=proforma)
        form = ProformaItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            proforma.recalcular_totales()
            return _items_and_totales_response(proforma, ProformaItemForm(), request)
        html = render_to_string(
            'proformas/partials/items_table.html',
            self._edit_context(proforma, item, form),
            request=request,
        )
        return HttpResponse(html)


class ProformaItemCancelEditView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'proformas.editar_proforma'
    def get(self, request, proforma_pk):
        proforma = get_object_or_404(Proforma, pk=proforma_pk, activo=True)
        return _items_and_totales_response(proforma, ProformaItemForm(), request)


# ── Conditions HTMX ──────────────────────────────────────────────────────────

class ProformaCondicionCreateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'proformas.editar_proforma'
    def post(self, request, proforma_pk):
        proforma = get_object_or_404(Proforma, pk=proforma_pk, activo=True)
        form = ProformaCondicionForm(request.POST)
        if form.is_valid():
            cond = form.save(commit=False)
            cond.proforma = proforma
            last = proforma.condiciones.aggregate(m=Max('orden'))['m'] or 0
            cond.orden = last + 1
            cond.save()
            return _condiciones_response(proforma, ProformaCondicionForm(), request)
        return _condiciones_response(proforma, form, request)


class ProformaCondicionDeleteView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'proformas.editar_proforma'
    def post(self, request, proforma_pk, cond_pk):
        proforma = get_object_or_404(Proforma, pk=proforma_pk, activo=True)
        cond = get_object_or_404(ProformaCondicion, pk=cond_pk, proforma=proforma)
        cond.delete()
        return _condiciones_response(proforma, ProformaCondicionForm(), request)


# ── Estado / Nueva versión ────────────────────────────────────────────────────

class ProformaEstadoView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'proformas.editar_proforma'
    def post(self, request, pk):
        proforma = get_object_or_404(Proforma, pk=pk, activo=True)
        nuevo = request.POST.get('estado')
        if nuevo in dict(Proforma.ESTADO_CHOICES):
            proforma.estado = nuevo
            proforma.save(update_fields=['estado'])
        return HttpResponseRedirect(
            reverse('proformas:proforma_detail', kwargs={'pk': proforma.pk})
        )


class ProformaMargenView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'proformas.editar_proforma'
    def post(self, request, pk):
        from decimal import Decimal, InvalidOperation
        proforma = get_object_or_404(Proforma, pk=pk, activo=True)
        try:
            margen = Decimal(request.POST.get('margen_objetivo', '0').replace(',', '.'))
            if Decimal('0') <= margen <= Decimal('500'):
                proforma.margen_objetivo = margen
                proforma.save(update_fields=['margen_objetivo'])
        except (InvalidOperation, ValueError):
            pass
        return HttpResponseRedirect(
            reverse('proformas:proforma_detail', kwargs={'pk': proforma.pk})
        )


class ProformaNuevaVersionView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'proformas.crear_proforma'
    def post(self, request, pk):
        original = get_object_or_404(Proforma, pk=pk, activo=True)
        Proforma.objects.filter(numero=original.numero, activo=True).update(es_vigente=False)
        nueva = Proforma.objects.create(
            numero=original.numero,
            version=original.version + 1,
            es_vigente=True,
            empresa=original.empresa,
            contacto=original.contacto,
            sede=original.sede,
            titulo=original.titulo,
            estado=Proforma.ESTADO_BORRADOR,
            tipo_cambio=original.tipo_cambio,
            tc_venta=original.tc_venta,
            fecha_emision=original.fecha_emision,
            validez_dias=original.validez_dias,
            incluye_igv=original.incluye_igv,
            porcentaje_igv=original.porcentaje_igv,
            observaciones=original.observaciones,
        )
        for item in original.items.all():
            ProformaItem.objects.create(
                proforma=nueva, orden=item.orden, servicio=item.servicio,
                descripcion=item.descripcion, descripcion_tecnica=item.descripcion_tecnica,
                unidad=item.unidad, cantidad=item.cantidad, precio_usd=item.precio_usd,
            )
        for cond in original.condiciones.all():
            ProformaCondicion.objects.create(
                proforma=nueva, condicion_ref=cond.condicion_ref, orden=cond.orden,
                titulo=cond.titulo, contenido=cond.contenido,
            )
        nueva.recalcular_totales()
        return HttpResponseRedirect(
            reverse('proformas:proforma_detail', kwargs={'pk': nueva.pk})
        )


# ── PDF view ──────────────────────────────────────────────────────────────────

class ProformaPDFView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = 'proformas.exportar_pdf'
    model = Proforma
    template_name = 'proformas/proforma_pdf.html'
    context_object_name = 'proforma'

    def get_queryset(self):
        return Proforma.objects.filter(activo=True).select_related(
            'empresa', 'contacto', 'sede', 'tipo_cambio__moneda',
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from decimal import Decimal
        from apps.catalogo.models import CuentaBancaria
        tc = self.object.tc_venta
        items = list(self.object.items.select_related('servicio', 'producto').all())
        if tc:
            for item in items:
                item.subtotal_pen = (item.subtotal_usd * tc).quantize(Decimal('0.01'))
        ctx['items'] = items
        ctx['condiciones'] = self.object.condiciones.all()
        ctx['cuentas'] = CuentaBancaria.objects.filter(activo=True)
        from apps.core.models import Configuracion
        ctx['config'] = Configuracion.get()
        return ctx


# ── HTMX helpers ─────────────────────────────────────────────────────────────

class ContactosByEmpresaView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'proformas.ver_proformas'
    def get(self, request):
        empresa_id = request.GET.get('empresa')
        contactos = Contacto.objects.none()
        sedes = Sede.objects.none()
        if empresa_id:
            contactos = Contacto.objects.filter(
                empresa_id=empresa_id, activo=True,
            ).order_by('-es_principal', 'nombre')
            sedes = Sede.objects.filter(
                empresa_id=empresa_id, activo=True,
            ).order_by('-es_principal', 'nombre')
        html = render_to_string(
            'proformas/partials/contacto_sede_options.html',
            {'contactos': contactos, 'sedes': sedes},
            request=request,
        )
        return HttpResponse(html)


class ServicioDataView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'proformas.ver_proformas'
    def get(self, request):
        servicio_id = request.GET.get('servicio')
        if servicio_id:
            from apps.catalogo.models import Servicio
            s = Servicio.objects.filter(pk=servicio_id, activo=True).first()
            if s:
                return JsonResponse({
                    'descripcion': s.nombre,
                    'descripcion_tecnica': s.descripcion,
                    'unidad': s.unidad,
                    'precio_usd': str(s.precio_usd),
                    'costo': str(s.costo) if s.costo is not None else '',
                    'moneda_costo': s.moneda_costo,
                })
        return JsonResponse({})


class CondicionDataView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'proformas.ver_proformas'
    def get(self, request):
        cond_id = request.GET.get('condicion')
        if cond_id:
            c = CondicionComercial.objects.filter(pk=cond_id, activo=True).first()
            if c:
                return JsonResponse({'titulo': c.nombre, 'contenido': c.contenido})
        return JsonResponse({})


class ProductoDataView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'proformas.ver_proformas'
    def get(self, request):
        producto_id = request.GET.get('producto')
        if producto_id:
            from apps.catalogo.models import Producto
            p = Producto.objects.filter(pk=producto_id, activo=True).first()
            if p:
                return JsonResponse({
                    'descripcion': str(p),
                    'descripcion_tecnica': p.descripcion_proforma,
                    'unidad': p.unidad,
                    'precio_usd': str(p.precio_usd),
                    'costo': str(p.costo) if p.costo is not None else '',
                    'moneda_costo': p.moneda_costo,
                })
        return JsonResponse({})
