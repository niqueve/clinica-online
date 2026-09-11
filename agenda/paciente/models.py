from django.db import models
from django.conf import settings
from core.models import EnderecoBase
from clinica.models import Clinica

class Paciente (EnderecoBase):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE, related_name='pacientes', null=True, 
    blank=True)

    cpf = models.CharField(max_length=14, unique=True, null=True, blank=True)
    telefone = models.CharField(max_length=20, null=True, blank=True)
    data_nascimento = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Paciente: {self.usuario.get_full_name() or self.usuario.username}"