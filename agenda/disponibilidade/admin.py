from django.contrib import admin
from .models import Disponibilidade

@admin.register(Disponibilidade)
class DisponibilidadeAdmin(admin.ModelAdmin):
    list_display = ('profissional', 'dia_semana', 'hora_inicio', 'hora_fim')
    list_filter = ('profissional', 'dia_semana')
