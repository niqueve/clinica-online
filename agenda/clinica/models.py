from django.db import models
from core.models import EnderecoBase

class Clinica(EnderecoBase):
    nome = models.CharField(max_length=200)
    cnpj = models.CharField(max_length=18, unique=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome