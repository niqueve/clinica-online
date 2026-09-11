from django.db import models
from django.contrib.auth.models import AbstractUser

class EnderecoBase (models.Model):
    rua = models.CharField(max_length=255)
    numero = models.CharField(max_length=20)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    cep = models.CharField(max_length=10)

    class Meta:
        abstract = True

class Usuario (AbstractUser):
    class TipoUsuario (models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        PACIENTE = 'PACIENTE', 'Paciente'
        PROFISSIONAL = 'PROFISSIONAL', 'Profissional'

    tipo = models.CharField(
        max_length=20,
        choices=TipoUsuario.choices,
        default=TipoUsuario.PACIENTE
    )

    def __str__(self):
        return f"{self.username} ({self.get_tipo_display()})"
