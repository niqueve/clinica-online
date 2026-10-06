from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

from clinica.views import ClinicaViewSet
from paciente.views import PacienteViewSet
from profissional.views import ProfissionalViewSet
from disponibilidade.views import DisponibilidadeViewSet
from consulta.views import ConsultaViewSet

router = DefaultRouter()
router.register(r'clinicas', ClinicaViewSet)
router.register(r'pacientes', PacienteViewSet)
router.register(r'profissionais', ProfissionalViewSet)
router.register(r'disponibilidades', DisponibilidadeViewSet)
router.register(r'consultas', ConsultaViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('api/', include(router.urls)),
    path('api/token/', obtain_auth_token),
]
