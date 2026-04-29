from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from .forms import ConfiguracionForm
from .models import Configuracion


class ConfiguracionView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'core.editar_configuracion'
    template_name = 'core/configuracion.html'

    def get(self, request):
        config = Configuracion.get()
        form = ConfiguracionForm(instance=config)
        return render(request, self.template_name, {'form': form, 'config': config})

    def post(self, request):
        config = Configuracion.get()
        form = ConfiguracionForm(request.POST, request.FILES, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configuración guardada correctamente.')
            return redirect('core:configuracion')
        return render(request, self.template_name, {'form': form, 'config': config})
