from django.contrib import admin
from .models import Clinica

@admin.register(Clinica)
class ClinicaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cnpj', 'cidade', 'criado_em')
    search_fields = ('nome', 'cnpj')
