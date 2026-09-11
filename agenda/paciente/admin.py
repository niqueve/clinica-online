from django.contrib import admin
from .models import Paciente

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'cpf', 'telefone', 'clinica')
    search_fields = ('cpf', 'telefone')
