from django.db import models
from django.conf import settings
from core.models import EnderecoBase
from clinica.models import Clinica

class Profissional(EnderecoBase):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE, related_name='profissionais', null=True, 
    blank=True)

    especialidade = models.CharField(max_length=100)
    registro_conselho = models.CharField(max_length=50, unique=True, null=True, blank=True)

    def __str__(self):
        return f"Dr(a). {self.usuario.get_full_name() or self.usuario.username} - {self.especialidade}"
