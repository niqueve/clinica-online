from django.urls import path
from .views import lista_consultas

app_name = 'consulta'

urlpatterns = [
    path('', lista_consultas, name='lista_consultas'),
]