from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings


class EnderecoBase(models.Model):
    rua = models.CharField(max_length=255)
    numero = models.CharField(max_length=20)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    cep = models.CharField(max_length=10)

    class Meta:
        abstract = True


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def criar_token_auth(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.get_or_create(user=instance)


class Usuario(AbstractUser):
    class TipoUsuario(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        PACIENTE = 'PACIENTE', 'Paciente'
        PROFISSIONAL = 'PROFISSIONAL', 'Profissional'
        CLINICA = 'CLINICA', 'Representante de Clínica'

    STATUS_CHOICES = (
        ('PENDENTE', 'Pendente de Aprovação'),
        ('APROVADO', 'Aprovado'),
        ('REJEITADO', 'Rejeitado'),
        ('DESATIVADO', 'Desativado'),
    )

    tipo = models.CharField(
        max_length=30,
        choices=TipoUsuario.choices,
        blank=True,
        null=True
    )

    status_aprovacao = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDENTE'
    )

    def __str__(self):
        return f"{self.username} ({self.get_tipo_display()})"