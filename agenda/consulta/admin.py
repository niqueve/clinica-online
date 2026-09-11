from django.contrib import admin
from .models import Consulta

@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'profissional', 'data_hora_inicio', 'data_hora_fim', 'status')
    list_filter = ('status', 'profissional', 'data_hora_inicio')