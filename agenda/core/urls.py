from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import (
    CustomLoginView, dashboard_view, home_view, RegisterAPIView,
    selecionar_perfil_view, SessionLoginAPIView, editar_perfil_view,
    agendar_consulta_view, cancelar_consulta_view, solicitar_profissional_view,
    aprovar_profissional_view, rejeitar_profissional_view,
)

app_name = 'core'

urlpatterns = [
    path('', home_view, name='home'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='core:home'), name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('perfil/editar/', editar_perfil_view, name='editar_perfil'),
    path('consultas/agendar/', agendar_consulta_view, name='agendar_consulta'),
    path('consultas/<int:consulta_id>/cancelar/', cancelar_consulta_view, name='cancelar_consulta'),
    path('selecionar-perfil/', selecionar_perfil_view, name='selecionar_perfil'),
    path('api/register/', RegisterAPIView.as_view(), name='api_register'),
    path('api/session-login/', SessionLoginAPIView.as_view(), name='session_login'),
    path('profissional/solicitar/', solicitar_profissional_view, name='solicitar_profissional'),
    path('admin/profissionais/<int:usuario_id>/aprovar/', aprovar_profissional_view, name='aprovar_profissional'),
    path('admin/profissionais/<int:usuario_id>/rejeitar/', rejeitar_profissional_view, name='rejeitar_profissional'),
]