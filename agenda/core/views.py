from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from consulta.models import Consulta
from paciente.models import Paciente
from profissional.models import Profissional
from clinica.models import Clinica
class CustomLoginView(LoginView):
    template_name = 'core/login.html'
    redirect_authenticated_user = True

    def get_sucess_url(self):
        return reverse_lazy('core:dashboard')


@login_required
def dashboard_view(request):
    user = request.user
    context = {}

    if user.is_superuser or (hasattr(user, 'tipo') and user.tipo == 'ADMIN'):
        context['total_consultas'] = Consulta.objects.count()
        context['total_pacientes'] = Paciente.objects.count()
        context['total_profissionais'] = Profissional.objects.count()
        context['total_clinicas'] = Clinica.objects.count()
        template_name = 'core/dashboard_admin.html'

    elif hasattr(user, 'tipo') and user.tipo == 'PROFISSIONAL':
        profissional = Profissional.objects.filter(usuario=user).first()
        context['consultas'] = Consulta.objects.filter(profissional=profissional) if profissional else []
        template_name = 'core/dashboard_profissional.html'

    else:
        paciente = Paciente.objects.filter(usuario=user).first()
        context['consultas'] = Consulta.objects.filter(paciente=paciente) if paciente else []
        template_name = 'core/dashboard_paciente.html'

    return render(request, template_name, context)