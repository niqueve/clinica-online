from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import CustomLoginView, dashboard_view, home_view, RegisterAPIView, selecionar_perfil_view, SessionLoginAPIView

app_name = 'core'

urlpatterns = [
    path('', home_view, name='home'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='core:home'), name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('selecionar-perfil/', selecionar_perfil_view, name='selecionar_perfil'),
    path('api/register/', RegisterAPIView.as_view(), name='api_register'),
    path('api/session-login/', SessionLoginAPIView.as_view(), name='session_login'),
]