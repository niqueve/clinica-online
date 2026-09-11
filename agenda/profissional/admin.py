from django.contrib import admin
from .models import Profissional

@admin.register(Profissional)
class ProfissionalAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'especialidade', 'registro_conselho', 'clinica')
    search_fields = ('registro_conselho', 'especialidade')
