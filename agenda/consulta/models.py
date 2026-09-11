from django.db import models
from paciente.models import Paciente
from profissional.models import Profissional

class Consulta(models.Model):
    STATUS_CHOICES = [
        ('AGENDADA', 'Agendada'),
        ('CONCLUIDA', 'Concluida'),
        ('CANCELADA', 'Cancelada'),
    ]

    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='consultas')
    profissional = models.ForeignKey(Profissional, on_delete=models.CASCADE, related_name='consultas')

    data_hora_inicio = models.DateTimeField()
    data_hora_fim = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AGENDADA')
    observacoes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Consulta: {self.paciente} com {self.profissional} em {self.data_hora_inicio.strftime('%d/%m/%Y %H:%M')}"
