from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from apps.core.models import Configuracion

from .forms import ArchivoRepositorioForm, CarpetaRepositorioForm, DocumentoGeneradoForm, PlantillaForm
from .models import ArchivoRepositorio, CarpetaRepositorio, DocumentoGenerado, PlantillaDocumento, TIPO_GRUPOS


# ── Plantillas ────────────────────────────────────────────────────────────────

class PlantillaListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'documentos.ver_documentos'
    model = PlantillaDocumento
    template_name = 'documentos/plantilla_list.html'
    context_object_name = 'plantillas'

    def get_queryset(self):
        qs = PlantillaDocumento.objects.filter(activo=True)
        tipo = self.request.GET.get('tipo')
        if tipo:
            qs = qs.filter(tipo=tipo)
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(nombre__icontains=q)
        return qs.order_by('tipo', 'nombre')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['tipo_grupos'] = TIPO_GRUPOS
        ctx['tipo_filtro'] = self.request.GET.get('tipo', '')
        ctx['q'] = self.request.GET.get('q', '')
        return ctx


class PlantillaCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'documentos.gestionar_plantillas'
    model = PlantillaDocumento
    form_class = PlantillaForm
    template_name = 'documentos/plantilla_form.html'
    success_url = reverse_lazy('documentos:plantilla_list')

    def form_valid(self, form):
        plantilla = form.save(commit=False)
        plantilla.creado_por = self.request.user
        plantilla.save()
        return HttpResponseRedirect(self.success_url)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo_pagina'] = 'Nueva plantilla'
        ctx['accion'] = 'Crear plantilla'
        from .models import VARIABLES_DISPONIBLES
        ctx['variables'] = VARIABLES_DISPONIBLES
        return ctx


class PlantillaUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'documentos.gestionar_plantillas'
    model = PlantillaDocumento
    form_class = PlantillaForm
    template_name = 'documentos/plantilla_form.html'
    success_url = reverse_lazy('documentos:plantilla_list')

    def get_queryset(self):
        return PlantillaDocumento.objects.filter(activo=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo_pagina'] = f'Editar plantilla — {self.object.nombre}'
        ctx['accion'] = 'Guardar cambios'
        from .models import VARIABLES_DISPONIBLES
        ctx['variables'] = VARIABLES_DISPONIBLES
        return ctx


class PlantillaDeleteView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'documentos.gestionar_plantillas'
    def post(self, request, pk):
        plantilla = get_object_or_404(PlantillaDocumento, pk=pk)
        plantilla.activo = False
        plantilla.save(update_fields=['activo'])
        return HttpResponseRedirect(reverse('documentos:plantilla_list'))


# ── Documentos generados ──────────────────────────────────────────────────────

class DocumentoListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'documentos.ver_documentos'
    model = DocumentoGenerado
    template_name = 'documentos/documento_list.html'
    context_object_name = 'documentos'
    paginate_by = 20

    def get_queryset(self):
        qs = DocumentoGenerado.objects.filter(activo=True).select_related(
            'proyecto', 'empresa', 'plantilla_origen',
        )
        tipo = self.request.GET.get('tipo')
        if tipo:
            qs = qs.filter(tipo=tipo)
        q = self.request.GET.get('q', '').strip()
        if q:
            from django.db.models import Q
            qs = qs.filter(
                Q(nombre__icontains=q) |
                Q(empresa__razon_social__icontains=q) |
                Q(proyecto__numero__icontains=q)
            )
        return qs.order_by('-created_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['tipo_grupos'] = TIPO_GRUPOS
        ctx['tipo_filtro'] = self.request.GET.get('tipo', '')
        ctx['q'] = self.request.GET.get('q', '')
        return ctx


class DocumentoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'documentos.crear_documento'
    model = DocumentoGenerado
    form_class = DocumentoGeneradoForm
    template_name = 'documentos/documento_form.html'

    def form_valid(self, form):
        doc = form.save(commit=False)
        doc.creado_por = self.request.user
        doc.save()
        return HttpResponseRedirect(
            reverse('documentos:documento_detail', kwargs={'pk': doc.pk})
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo_pagina'] = 'Nuevo documento'
        ctx['accion'] = 'Crear documento'
        from .models import VARIABLES_DISPONIBLES
        ctx['variables'] = VARIABLES_DISPONIBLES
        return ctx


class DocumentoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'documentos.editar_documento'
    model = DocumentoGenerado
    form_class = DocumentoGeneradoForm
    template_name = 'documentos/documento_form.html'

    def get_queryset(self):
        return DocumentoGenerado.objects.filter(activo=True)

    def get_success_url(self):
        return reverse('documentos:documento_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo_pagina'] = f'Editar — {self.object.nombre}'
        ctx['accion'] = 'Guardar cambios'
        from .models import VARIABLES_DISPONIBLES
        ctx['variables'] = VARIABLES_DISPONIBLES
        return ctx


class DocumentoDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = 'documentos.ver_documentos'
    model = DocumentoGenerado
    template_name = 'documentos/documento_detail.html'
    context_object_name = 'doc'

    def get_queryset(self):
        return DocumentoGenerado.objects.filter(activo=True).select_related(
            'proyecto', 'empresa', 'plantilla_origen', 'creado_por',
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from apps.proyectos.models import Proyecto
        ctx['proyectos_disponibles'] = Proyecto.objects.filter(activo=True).order_by('-created_at').select_related('empresa')
        return ctx


class DocumentoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'documentos.eliminar_documento'
    def post(self, request, pk):
        doc = get_object_or_404(DocumentoGenerado, pk=pk, activo=True)
        doc.activo = False
        doc.save(update_fields=['activo'])
        return HttpResponseRedirect(reverse('documentos:documento_list'))


class DocumentoPrintView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = 'documentos.ver_documentos'
    model = DocumentoGenerado
    template_name = 'documentos/documento_print.html'
    context_object_name = 'doc'

    def get_queryset(self):
        return DocumentoGenerado.objects.filter(activo=True).select_related(
            'proyecto', 'empresa',
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['config'] = Configuracion.get()
        return ctx


# ── Generar desde plantilla ───────────────────────────────────────────────────

class GenerarDesdeProyectoView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'documentos.crear_documento'
    def post(self, request, plantilla_pk, proyecto_pk):
        from apps.proyectos.models import Proyecto
        plantilla = get_object_or_404(PlantillaDocumento, pk=plantilla_pk, activo=True)
        proyecto = get_object_or_404(Proyecto, pk=proyecto_pk, activo=True)
        doc = plantilla.generar_para_proyecto(proyecto, usuario=request.user)
        return HttpResponseRedirect(
            reverse('documentos:documento_detail', kwargs={'pk': doc.pk})
        )


class DocumentoVincularView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'documentos.editar_documento'
    """Link or unlink a DocumentoGenerado to/from a Proyecto."""
    def post(self, request, pk):
        doc = get_object_or_404(DocumentoGenerado, pk=pk, activo=True)
        proyecto_id = request.POST.get('proyecto')
        if proyecto_id:
            from apps.proyectos.models import Proyecto
            proyecto = Proyecto.objects.filter(pk=proyecto_id, activo=True).first()
            doc.proyecto = proyecto
        else:
            doc.proyecto = None
        doc.save(update_fields=['proyecto'])
        return HttpResponseRedirect(
            reverse('documentos:documento_detail', kwargs={'pk': doc.pk})
        )


class GenerarStandaloneView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'documentos.crear_documento'
    def get(self, request, plantilla_pk):
        from django.shortcuts import render
        plantilla = get_object_or_404(PlantillaDocumento, pk=plantilla_pk, activo=True)
        from apps.clientes.models import Empresa
        empresas = Empresa.objects.filter(activo=True).order_by('razon_social')
        return render(request, 'documentos/generar_standalone.html', {
            'plantilla': plantilla,
            'empresas': empresas,
        })

    def post(self, request, plantilla_pk):
        plantilla = get_object_or_404(PlantillaDocumento, pk=plantilla_pk, activo=True)
        empresa_id = request.POST.get('empresa')
        empresa = None
        if empresa_id:
            from apps.clientes.models import Empresa
            empresa = Empresa.objects.filter(pk=empresa_id, activo=True).first()
        doc = plantilla.generar_standalone(empresa=empresa, usuario=request.user)
        return HttpResponseRedirect(
            reverse('documentos:documento_detail', kwargs={'pk': doc.pk})
        )


# ── Repositorio de archivos ───────────────────────────────────────────────────

class RepositorioView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'documentos.ver_documentos'

    def get(self, request):
        carpeta_id = request.GET.get('carpeta')
        carpeta_actual = None
        if carpeta_id:
            carpeta_actual = get_object_or_404(CarpetaRepositorio, pk=carpeta_id, activo=True)

        subcarpetas = CarpetaRepositorio.objects.filter(
            carpeta_padre=carpeta_actual, activo=True,
        ).order_by('nombre')
        archivos = ArchivoRepositorio.objects.filter(
            carpeta=carpeta_actual, activo=True,
        ).order_by('nombre')
        ancestors = carpeta_actual.get_ancestors() if carpeta_actual else []

        carpeta_form = CarpetaRepositorioForm(initial={'carpeta_padre': carpeta_actual})
        archivo_form = ArchivoRepositorioForm(carpeta_inicial=carpeta_actual)

        return render(request, 'documentos/repositorio.html', {
            'carpeta_actual': carpeta_actual,
            'subcarpetas': subcarpetas,
            'archivos': archivos,
            'ancestors': ancestors,
            'carpeta_form': carpeta_form,
            'archivo_form': archivo_form,
        })


class CarpetaCreateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'documentos.gestionar_repositorio'

    def post(self, request):
        form = CarpetaRepositorioForm(request.POST)
        carpeta_padre_id = request.POST.get('carpeta_padre') or None
        if form.is_valid():
            carpeta = form.save(commit=False)
            carpeta.creado_por = request.user
            carpeta.save()
        redirect_url = reverse('documentos:repositorio')
        if carpeta_padre_id:
            redirect_url += f'?carpeta={carpeta_padre_id}'
        return HttpResponseRedirect(redirect_url)


class CarpetaDeleteView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'documentos.gestionar_repositorio'

    def post(self, request, pk):
        carpeta = get_object_or_404(CarpetaRepositorio, pk=pk, activo=True)
        padre_id = carpeta.carpeta_padre_id
        carpeta.activo = False
        carpeta.save(update_fields=['activo'])
        redirect_url = reverse('documentos:repositorio')
        if padre_id:
            redirect_url += f'?carpeta={padre_id}'
        return HttpResponseRedirect(redirect_url)


class ArchivoSubirView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'documentos.gestionar_repositorio'

    def post(self, request):
        from django.http import JsonResponse
        import os
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        form = ArchivoRepositorioForm(request.POST, request.FILES)
        carpeta_id = request.POST.get('carpeta') or None
        if form.is_valid():
            archivo = form.save(commit=False)
            # Auto-fill nombre from filename when not provided
            if not archivo.nombre and archivo.archivo:
                archivo.nombre = os.path.splitext(os.path.basename(archivo.archivo.name))[0]
            archivo.subido_por = request.user
            if archivo.archivo:
                archivo.tamano_bytes = archivo.archivo.size
            archivo.save()
            if is_ajax:
                return JsonResponse({'ok': True, 'nombre': archivo.nombre, 'pk': archivo.pk})
        else:
            if is_ajax:
                return JsonResponse({'ok': False, 'errors': form.errors}, status=400)
        redirect_url = reverse('documentos:repositorio')
        if carpeta_id:
            redirect_url += f'?carpeta={carpeta_id}'
        return HttpResponseRedirect(redirect_url)


class ArchivoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'documentos.gestionar_repositorio'

    def post(self, request, pk):
        archivo = get_object_or_404(ArchivoRepositorio, pk=pk, activo=True)
        carpeta_id = archivo.carpeta_id
        archivo.activo = False
        archivo.save(update_fields=['activo'])
        redirect_url = reverse('documentos:repositorio')
        if carpeta_id:
            redirect_url += f'?carpeta={carpeta_id}'
        return HttpResponseRedirect(redirect_url)
