from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.clientes.models import Contacto, Sede

from .forms import (ActividadForm, ActividadQuickForm, ComentarioActividadForm,
                    ColumnaKanbanForm, DocumentoForm, ProyectoForm,
                    RegistroTiempoForm, TecnicoAsignadoForm)
from .models import (Actividad, ComentarioActividad, ColumnaKanban, Documento,
                     Proyecto, RegistroTiempo, TecnicoAsignado)


def _tecnicos_response(proyecto, form, request):
    proyecto.refresh_from_db()
    html = render_to_string(
        'proyectos/partials/tecnicos_section.html',
        {
            'proyecto': proyecto,
            'asignaciones': proyecto.tecnicos.select_related('tecnico').all(),
            'tecnico_form': form,
        },
        request=request,
    )
    return HttpResponse(html)


def _documentos_response(proyecto, form, request):
    proyecto.refresh_from_db()
    html = render_to_string(
        'proyectos/partials/documentos_section.html',
        {
            'proyecto': proyecto,
            'documentos': proyecto.documentos.filter(activo=True).select_related('tecnico').order_by('-created_at'),
            'documento_form': form,
            'docs_generados': proyecto.documentos_generados.filter(activo=True).order_by('-created_at'),
        },
        request=request,
    )
    return HttpResponse(html)


# ── List ─────────────────────────────────────────────────────────────────────

class ProyectoListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'proyectos.ver_proyectos'
    model = Proyecto
    template_name = 'proyectos/proyecto_list.html'
    context_object_name = 'proyectos'
    paginate_by = 20

    def get_queryset(self):
        qs = Proyecto.objects.filter(activo=True).select_related('empresa', 'contacto')
        estado = self.request.GET.get('estado', '')
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
        ctx['estado_choices'] = Proyecto.ESTADO_CHOICES
        ctx['estado_filtro'] = self.request.GET.get('estado', '')
        ctx['q'] = self.request.GET.get('q', '')
        base = Proyecto.objects.filter(activo=True)
        ctx['totals'] = {
            'total': base.count(),
            'activos': base.filter(estado__in=[Proyecto.ESTADO_ACTIVO, Proyecto.ESTADO_EN_EJECUCION]).count(),
            'completados': base.filter(estado=Proyecto.ESTADO_COMPLETADO).count(),
            'pendientes': base.filter(estado=Proyecto.ESTADO_PENDIENTE_FIRMA).count(),
        }
        return ctx


# ── Create / Update ───────────────────────────────────────────────────────────

class ProyectoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'proyectos.crear_proyecto'
    model = Proyecto
    form_class = ProyectoForm
    template_name = 'proyectos/proyecto_form.html'

    def form_valid(self, form):
        proyecto = form.save(commit=False)
        proyecto.numero = Proyecto.generar_numero()
        if proyecto.tc_venta and not proyecto.valor_pen:
            from decimal import Decimal
            proyecto.valor_pen = (proyecto.valor_usd * proyecto.tc_venta).quantize(Decimal('0.01'))
        proyecto.save()
        ColumnaKanban.crear_defaults(proyecto)
        messages.success(self.request, f'Proyecto {proyecto.numero} creado.')
        return HttpResponseRedirect(reverse('proyectos:proyecto_detail', kwargs={'pk': proyecto.pk}))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo_pagina'] = 'Nuevo Proyecto'
        ctx['accion'] = 'Crear proyecto'
        return ctx


class ProyectoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'proyectos.editar_proyecto'
    model = Proyecto
    form_class = ProyectoForm
    template_name = 'proyectos/proyecto_form.html'

    def get_queryset(self):
        return Proyecto.objects.filter(activo=True)

    def form_valid(self, form):
        proyecto = form.save()
        messages.success(self.request, 'Proyecto actualizado.')
        return HttpResponseRedirect(reverse('proyectos:proyecto_detail', kwargs={'pk': proyecto.pk}))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo_pagina'] = 'Editar Proyecto'
        ctx['accion'] = 'Guardar cambios'
        return ctx


# ── Detail ────────────────────────────────────────────────────────────────────

class ProyectoDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = 'proyectos.ver_proyectos'
    model = Proyecto
    template_name = 'proyectos/proyecto_detail.html'
    context_object_name = 'proyecto'

    def get_queryset(self):
        return Proyecto.objects.filter(activo=True).select_related(
            'empresa', 'contacto', 'sede', 'proforma',
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['asignaciones'] = self.object.tecnicos.select_related('tecnico').all()
        ctx['documentos'] = self.object.documentos.filter(activo=True).select_related('tecnico').order_by('-created_at')
        ctx['tecnico_form'] = TecnicoAsignadoForm(proyecto=self.object)
        ctx['documento_form'] = DocumentoForm()
        ctx['sctr_valido'] = self.object.sctr_valido
        ctx['estado_choices'] = Proyecto.ESTADO_CHOICES
        ctx['docs_generados'] = self.object.documentos_generados.filter(activo=True).order_by('-created_at')
        # Kanban — usa _kanban_ctx para tener pk, css y es_final en cada columna
        ctx.update(_kanban_ctx(self.object))
        from django.db.models import Sum
        ctx['total_horas'] = (
            RegistroTiempo.objects
            .filter(actividad__proyecto=self.object, actividad__activo=True)
            .aggregate(total=Sum('horas'))['total'] or 0
        )
        return ctx


# ── Delete ────────────────────────────────────────────────────────────────────

class ProyectoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'proyectos.eliminar_proyecto'
    model = Proyecto
    template_name = 'proyectos/proyecto_confirm_delete.html'
    success_url = reverse_lazy('proyectos:proyecto_list')

    def form_valid(self, form):
        self.object = self.get_object()
        self.object.activo = False
        self.object.save()
        messages.success(self.request, f'Proyecto {self.object.numero} archivado.')
        return HttpResponseRedirect(self.success_url)


# ── Estado ────────────────────────────────────────────────────────────────────

class ProyectoEstadoView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'proyectos.editar_proyecto'
    def post(self, request, pk):
        proyecto = get_object_or_404(Proyecto, pk=pk, activo=True)
        nuevo = request.POST.get('estado')
        if nuevo not in dict(Proyecto.ESTADO_CHOICES):
            messages.error(request, 'Estado no válido.')
            return HttpResponseRedirect(reverse('proyectos:proyecto_detail', kwargs={'pk': pk}))

        # HU16: bloquear en_ejecucion si SCTR inválido
        if nuevo == Proyecto.ESTADO_EN_EJECUCION and not proyecto.sctr_valido:
            messages.error(
                request,
                'No se puede iniciar la ejecución: hay técnicos asignados sin SCTR válido o con SCTR vencido.',
            )
            return HttpResponseRedirect(reverse('proyectos:proyecto_detail', kwargs={'pk': pk}))

        proyecto.estado = nuevo
        proyecto.save(update_fields=['estado'])
        return HttpResponseRedirect(reverse('proyectos:proyecto_detail', kwargs={'pk': pk}))


# ── Desde Proforma (HU13) ─────────────────────────────────────────────────────

class ProyectoFromProformaView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'proyectos.crear_proyecto'
    def post(self, request, proforma_pk):
        from apps.proformas.models import Proforma
        proforma = get_object_or_404(Proforma, pk=proforma_pk, activo=True)

        # Check if project already exists for this proforma
        existing = Proyecto.objects.filter(proforma=proforma, activo=True).first()
        if existing:
            messages.info(request, f'La proforma ya tiene el proyecto {existing.numero}.')
            return HttpResponseRedirect(reverse('proyectos:proyecto_detail', kwargs={'pk': existing.pk}))

        proyecto = Proyecto.objects.create(
            numero=Proyecto.generar_numero(),
            proforma=proforma,
            empresa=proforma.empresa,
            contacto=proforma.contacto,
            sede=proforma.sede,
            titulo=proforma.titulo,
            estado=Proyecto.ESTADO_BORRADOR,
            valor_usd=proforma.total_usd,
            valor_pen=proforma.total_pen,
            tc_venta=proforma.tc_venta,
        )
        ColumnaKanban.crear_defaults(proyecto)
        messages.success(request, f'Proyecto {proyecto.numero} creado desde proforma {proforma.numero}.')
        return HttpResponseRedirect(reverse('proyectos:proyecto_detail', kwargs={'pk': proyecto.pk}))


# ── Contrato HTML (HU14) ──────────────────────────────────────────────────────

class ProyectoContratoView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = 'proyectos.ver_proyectos'
    model = Proyecto
    template_name = 'proyectos/proyecto_contrato.html'
    context_object_name = 'proyecto'

    def get_queryset(self):
        return Proyecto.objects.filter(activo=True).select_related(
            'empresa', 'contacto', 'sede',
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['asignaciones'] = self.object.tecnicos.select_related('tecnico').all()
        from apps.catalogo.models import CuentaBancaria
        ctx['cuentas'] = CuentaBancaria.objects.filter(activo=True)
        return ctx


# ── Técnicos HTMX (HU15) ─────────────────────────────────────────────────────

class TecnicoCreateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'proyectos.editar_proyecto'
    def post(self, request, proyecto_pk):
        proyecto = get_object_or_404(Proyecto, pk=proyecto_pk, activo=True)
        form = TecnicoAsignadoForm(request.POST, proyecto=proyecto)
        if form.is_valid():
            asig = form.save(commit=False)
            asig.proyecto = proyecto
            asig.save()
        return _tecnicos_response(proyecto, TecnicoAsignadoForm(proyecto=proyecto), request)


class TecnicoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'proyectos.editar_proyecto'
    def post(self, request, proyecto_pk, asig_pk):
        proyecto = get_object_or_404(Proyecto, pk=proyecto_pk, activo=True)
        asig = get_object_or_404(TecnicoAsignado, pk=asig_pk, proyecto=proyecto)
        asig.delete()
        return _tecnicos_response(proyecto, TecnicoAsignadoForm(proyecto=proyecto), request)


# ── Documentos HTMX ──────────────────────────────────────────────────────────

class DocumentoCreateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'proyectos.editar_proyecto'

    def post(self, request, proyecto_pk):
        proyecto = get_object_or_404(Proyecto, pk=proyecto_pk, activo=True)
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.proyecto = proyecto
            doc.save()
            return _documentos_response(proyecto, DocumentoForm(), request)
        return _documentos_response(proyecto, form, request)


class DocumentoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'proyectos.editar_proyecto'

    def post(self, request, proyecto_pk, doc_pk):
        proyecto = get_object_or_404(Proyecto, pk=proyecto_pk, activo=True)
        doc = get_object_or_404(Documento, pk=doc_pk, proyecto=proyecto)
        doc.activo = False
        doc.save(update_fields=['activo'])
        return _documentos_response(proyecto, DocumentoForm(), request)


# ── HTMX helpers ─────────────────────────────────────────────────────────────

class ProformaDataView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'proyectos.ver_proyectos'

    def get(self, request):
        from apps.proformas.models import Proforma
        proforma_id = request.GET.get('proforma')
        if proforma_id:
            p = (
                Proforma.objects
                .filter(pk=proforma_id, activo=True)
                .select_related('empresa', 'contacto', 'sede')
                .first()
            )
            if p:
                return JsonResponse({
                    'empresa_id': p.empresa_id,
                    'empresa_nombre': str(p.empresa),
                    'contacto_id': p.contacto_id,
                    'sede_id': p.sede_id,
                    'valor_usd': str(p.total_usd),
                    'tc_venta': str(p.tc_venta) if p.tc_venta else '',
                    'valor_pen': str(p.total_pen),
                    'titulo': p.titulo,
                })
        return JsonResponse({})


class ContactosByEmpresaView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'proyectos.ver_proyectos'

    def get(self, request):
        empresa_id = request.GET.get('empresa')
        contactos = Contacto.objects.none()
        sedes = Sede.objects.none()
        if empresa_id:
            contactos = Contacto.objects.filter(empresa_id=empresa_id, activo=True).order_by('-es_principal', 'nombre')
            sedes = Sede.objects.filter(empresa_id=empresa_id, activo=True).order_by('-es_principal', 'nombre')
        html = render_to_string(
            'proyectos/partials/contacto_sede_options.html',
            {'contactos': contactos, 'sedes': sedes},
            request=request,
        )
        return HttpResponse(html)


# ── Kanban — Actividades ──────────────────────────────────────────────────────

def _kanban_ctx(proyecto):
    actividades = proyecto.actividades.filter(activo=True).select_related('responsable').order_by('orden', 'created_at')
    columnas    = list(proyecto.columnas_kanban.filter(activo=True).order_by('orden'))
    actos_list  = list(actividades)
    final_slugs = {c.slug for c in columnas if c.es_final}
    return {
        'proyecto': proyecto,
        'kanban_columnas': [
            {
                'pk':          col.pk,
                'estado':      col.slug,
                'label':       col.nombre,
                'css':         col.css,
                'es_final':    col.es_final,
                'actividades': [a for a in actos_list if a.estado == col.slug],
            }
            for col in columnas
        ],
        'columna_form':      ColumnaKanbanForm(),
        'actividad_form':    ActividadForm(proyecto=proyecto),
        'total_actividades': len(actos_list),
        'completadas':       sum(1 for a in actos_list if a.estado in final_slugs),
    }


def _kanban_response(request, proyecto):
    html = render_to_string('proyectos/partials/kanban_board.html', _kanban_ctx(proyecto), request=request)
    return HttpResponse(html)


def _panel_ctx(proyecto, actividad):
    return {
        'proyecto':         proyecto,
        'actividad':        actividad,
        'form':             ActividadForm(instance=actividad, proyecto=proyecto),
        'comentarios':      actividad.comentarios.select_related('autor').all(),
        'comentario_form':  ComentarioActividadForm(),
        'registros_tiempo': actividad.registros_tiempo.select_related('usuario').all(),
        'tiempo_form':      RegistroTiempoForm(),
    }


class ActividadCreateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'proyectos.gestionar_actividades'

    def post(self, request, proyecto_pk):
        proyecto = get_object_or_404(Proyecto, pk=proyecto_pk, activo=True)
        # Quick create: only titulo + estado
        titulo  = request.POST.get('titulo', '').strip()
        estado  = request.POST.get('estado', Actividad.ESTADO_PENDIENTE)
        if titulo:
            ultimo_orden = proyecto.actividades.filter(estado=estado, activo=True).count()
            Actividad.objects.create(
                proyecto=proyecto, titulo=titulo, estado=estado, orden=ultimo_orden,
            )
        return _kanban_response(request, proyecto)


class ActividadUpdateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'proyectos.gestionar_actividades'

    def get(self, request, proyecto_pk, pk):
        proyecto  = get_object_or_404(Proyecto, pk=proyecto_pk, activo=True)
        actividad = get_object_or_404(Actividad, pk=pk, proyecto=proyecto, activo=True)
        return render(request, 'proyectos/partials/actividad_panel.html', _panel_ctx(proyecto, actividad))

    def post(self, request, proyecto_pk, pk):
        proyecto  = get_object_or_404(Proyecto, pk=proyecto_pk, activo=True)
        actividad = get_object_or_404(Actividad, pk=pk, proyecto=proyecto, activo=True)
        form      = ActividadForm(request.POST, instance=actividad, proyecto=proyecto)
        if form.is_valid():
            form.save()
            actividad.refresh_from_db()
            panel_html  = render_to_string('proyectos/partials/actividad_panel.html', _panel_ctx(proyecto, actividad), request=request)
            kanban_html = render_to_string('proyectos/partials/kanban_board.html', _kanban_ctx(proyecto), request=request)
            oob = f'<div hx-swap-oob="innerHTML:#kanban-wrapper">{kanban_html}</div>'
            return HttpResponse(panel_html + oob)
        ctx = _panel_ctx(proyecto, actividad)
        ctx['form'] = form
        return render(request, 'proyectos/partials/actividad_panel.html', ctx)


class ActividadDeleteView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'proyectos.gestionar_actividades'

    def post(self, request, proyecto_pk, pk):
        proyecto  = get_object_or_404(Proyecto, pk=proyecto_pk, activo=True)
        actividad = get_object_or_404(Actividad, pk=pk, proyecto=proyecto, activo=True)
        actividad.activo = False
        actividad.save(update_fields=['activo'])
        return _kanban_response(request, proyecto)


class ActividadMoverView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """Drag-and-drop: updates estado + orden via fetch JSON."""
    permission_required = 'proyectos.gestionar_actividades'

    def post(self, request, proyecto_pk, pk):
        proyecto  = get_object_or_404(Proyecto, pk=proyecto_pk, activo=True)
        actividad = get_object_or_404(Actividad, pk=pk, proyecto=proyecto, activo=True)
        import json
        try:
            data   = json.loads(request.body)
            estado = data.get('estado', actividad.estado)
            orden  = int(data.get('orden', actividad.orden))
        except (ValueError, KeyError):
            return JsonResponse({'ok': False}, status=400)
        valid_slugs = set(proyecto.columnas_kanban.filter(activo=True).values_list('slug', flat=True))
        if estado not in valid_slugs:
            return JsonResponse({'ok': False}, status=400)
        actividad.estado = estado
        actividad.orden  = orden
        actividad.save(update_fields=['estado', 'orden'])
        return JsonResponse({'ok': True})


class ComentarioCreateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'proyectos.ver_actividades'

    def post(self, request, proyecto_pk, actividad_pk):
        proyecto  = get_object_or_404(Proyecto, pk=proyecto_pk, activo=True)
        actividad = get_object_or_404(Actividad, pk=actividad_pk, proyecto=proyecto, activo=True)
        form      = ComentarioActividadForm(request.POST)
        if form.is_valid():
            c = form.save(commit=False)
            c.actividad = actividad
            c.autor     = request.user
            c.save()
        return render(request, 'proyectos/partials/actividad_panel.html', _panel_ctx(proyecto, actividad))


# ── Gantt PDF ────────────────────────────────────────────────────────────────

class ProyectoGanttPDFView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = 'proyectos.ver_proyectos'
    model = Proyecto
    template_name = 'proyectos/proyecto_gantt_pdf.html'
    context_object_name = 'proyecto'

    def get_queryset(self):
        return Proyecto.objects.filter(activo=True).select_related('empresa')

    def get_context_data(self, **kwargs):
        from datetime import date, timedelta
        from collections import OrderedDict
        from apps.core.models import Configuracion
        ctx = super().get_context_data(**kwargs)
        ctx['config'] = Configuracion.get()

        actividades_qs = self.object.actividades.filter(activo=True).select_related(
            'responsable'
        ).order_by('orden', 'created_at')

        hoy = date.today()
        actividades = []
        min_date = None
        max_date = None

        estado_labels = dict(Actividad.ESTADO_CHOICES)

        for act in actividades_qs:
            start = act.fecha_inicio or hoy
            end = act.fecha_vencimiento or start

            if end < start:
                end = start

            dur = (end - start).days + 1 if start != end else 1

            if min_date is None or start < min_date:
                min_date = start
            if max_date is None or end > max_date:
                max_date = end

            actividades.append({
                'titulo': act.titulo,
                'grupo': act.grupo,
                'responsable': act.responsable,
                'estado_slug': act.estado,
                'estado_label': estado_labels.get(act.estado, act.estado),
                'fecha_inicio': start,
                'fecha_fin': end,
                'fecha_inicio_fmt': start.strftime('%d/%m/%Y') if act.fecha_inicio else '—',
                'fecha_fin_fmt': end.strftime('%d/%m/%Y') if act.fecha_vencimiento else '—',
                'duracion_dias': dur if act.fecha_inicio else '—',
                'progreso': act.progreso,
                'left_pct': None,
                'width_pct': None,
            })

        has_dates = min_date is not None and max_date is not None
        if has_dates:
            total_days = (max_date - min_date).days or 1
            for item in actividades:
                if item['fecha_inicio'] and item['fecha_fin']:
                    left = ((item['fecha_inicio'] - min_date).days / total_days) * 100
                    width = max(((item['fecha_fin'] - item['fecha_inicio']).days + 1) / total_days * 100, 1.5)
                    item['left_pct'] = f'{left:.1f}'
                    item['width_pct'] = f'{width:.1f}'

            mid_date = min_date + timedelta(days=total_days // 2)
            ctx['range_start_fmt'] = min_date.strftime('%d/%m/%Y')
            ctx['range_mid_fmt'] = mid_date.strftime('%d/%m/%Y') if total_days > 7 else ''
            ctx['range_end_fmt'] = max_date.strftime('%d/%m/%Y')

        ctx['actividades'] = actividades
        ctx['has_dates'] = has_dates

        grupos = OrderedDict()
        for act in actividades:
            g = act['grupo'] or ''
            grupos.setdefault(g, []).append(act)
        ctx['grupos'] = grupos

        return ctx


class ProyectoGanttPDFDownloadView(ProyectoGanttPDFView):
    """Genera y descarga el PDF directamente usando xhtml2pdf."""
    template_name = 'proyectos/proyecto_gantt_pdf_download.html'

    def get(self, request, *args, **kwargs):
        from io import BytesIO
        from pathlib import Path
        from xhtml2pdf import pisa
        from django.conf import settings as django_settings

        self.object = self.get_object()
        ctx = self.get_context_data()
        ctx['request'] = request
        config = ctx['config']
        if config.logo:
            logo_file = Path(django_settings.MEDIA_ROOT) / config.logo.name
            ctx['logo_path'] = str(logo_file)
        html_string = render_to_string(self.template_name, ctx, request=request)
        buf = BytesIO()
        pisa.CreatePDF(html_string, dest=buf, encoding='utf-8')
        buf.seek(0)
        filename = f'Gantt_{ctx["proyecto"].numero}.pdf'
        response = HttpResponse(buf.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


# ── Gantt (Fase 2) ────────────────────────────────────────────────────────────

class GanttDataView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'proyectos.ver_actividades'

    def get(self, request, proyecto_pk):
        from datetime import date, timedelta
        proyecto    = get_object_or_404(Proyecto, pk=proyecto_pk, activo=True)
        actividades = proyecto.actividades.filter(activo=True).order_by('orden', 'created_at')
        hoy  = date.today()
        tasks = []
        for act in actividades:
            start = act.fecha_inicio or hoy
            end   = act.fecha_vencimiento or (start + timedelta(days=7))
            if end < start:
                end = start + timedelta(days=1)
            tasks.append({
                'id':           str(act.pk),
                'name':         act.titulo,
                'start':        start.strftime('%Y-%m-%d'),
                'end':          end.strftime('%Y-%m-%d'),
                'progress':     act.progreso,
                'custom_class': f'gantt-bar-{act.estado}',
            })
        return JsonResponse({'tasks': tasks})


class ActividadFechasView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'proyectos.gestionar_actividades'

    def post(self, request, proyecto_pk, pk):
        import json
        from datetime import datetime
        proyecto  = get_object_or_404(Proyecto, pk=proyecto_pk, activo=True)
        actividad = get_object_or_404(Actividad, pk=pk, proyecto=proyecto, activo=True)
        try:
            data  = json.loads(request.body)
            start = datetime.strptime(data['start'][:10], '%Y-%m-%d').date()
            end   = datetime.strptime(data['end'][:10], '%Y-%m-%d').date()
        except (KeyError, ValueError):
            return JsonResponse({'ok': False}, status=400)
        actividad.fecha_inicio      = start
        actividad.fecha_vencimiento = end
        actividad.save(update_fields=['fecha_inicio', 'fecha_vencimiento'])
        return JsonResponse({'ok': True})


# ── Registro de tiempo (Fase 2) ───────────────────────────────────────────────

class RegistroTiempoCreateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'proyectos.gestionar_actividades'

    def post(self, request, proyecto_pk, actividad_pk):
        proyecto  = get_object_or_404(Proyecto, pk=proyecto_pk, activo=True)
        actividad = get_object_or_404(Actividad, pk=actividad_pk, proyecto=proyecto, activo=True)
        form      = RegistroTiempoForm(request.POST)
        if form.is_valid():
            registro          = form.save(commit=False)
            registro.actividad = actividad
            registro.usuario   = request.user
            registro.save()
        return render(request, 'proyectos/partials/actividad_panel.html', _panel_ctx(proyecto, actividad))


class RegistroTiempoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'proyectos.gestionar_actividades'

    def post(self, request, proyecto_pk, actividad_pk, pk):
        proyecto  = get_object_or_404(Proyecto, pk=proyecto_pk, activo=True)
        actividad = get_object_or_404(Actividad, pk=actividad_pk, proyecto=proyecto, activo=True)
        registro  = get_object_or_404(RegistroTiempo, pk=pk, actividad=actividad)
        registro.delete()
        return render(request, 'proyectos/partials/actividad_panel.html', _panel_ctx(proyecto, actividad))


# ── Columnas Kanban (dinámicas) ───────────────────────────────────────────────

class ColumnaKanbanCreateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'proyectos.gestionar_actividades'

    def post(self, request, proyecto_pk):
        from django.utils.text import slugify
        proyecto = get_object_or_404(Proyecto, pk=proyecto_pk, activo=True)
        form     = ColumnaKanbanForm(request.POST)
        if form.is_valid():
            base_slug = slugify(form.cleaned_data['nombre']).replace('-', '_')[:45]
            slug, n   = base_slug, 1
            while proyecto.columnas_kanban.filter(slug=slug).exists():
                slug = f'{base_slug}_{n}'; n += 1
            col        = form.save(commit=False)
            col.proyecto = proyecto
            col.slug   = slug
            col.orden  = proyecto.columnas_kanban.filter(activo=True).count()
            col.save()
        return _kanban_response(request, proyecto)


class ColumnaKanbanDeleteView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'proyectos.gestionar_actividades'

    def post(self, request, proyecto_pk, pk):
        proyecto = get_object_or_404(Proyecto, pk=proyecto_pk, activo=True)
        col      = get_object_or_404(ColumnaKanban, pk=pk, proyecto=proyecto)
        tiene_actividades = proyecto.actividades.filter(estado=col.slug, activo=True).exists()
        if tiene_actividades:
            # Devuelve el board sin cambios; el template mostrará el error vía HX-Trigger
            resp = _kanban_response(request, proyecto)
            resp['HX-Trigger'] = f'{{"showError":"La columna «{col.nombre}» tiene actividades. Muévelas antes de eliminarla."}}'
            return resp
        col.activo = False
        col.save(update_fields=['activo'])
        return _kanban_response(request, proyecto)
