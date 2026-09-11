from django.db import models
from profissional.models import Profissional

class Disponibilidade(models.Model):
    DIAS_DA_SEMANA = [
        (0, 'Domingo'),
        (1, 'Segunda-feira'),
        (2, 'Terça-feira'),
        (3, 'Quarta-feira'),
        (4, 'Quinta-feira'),
        (5, 'Sexta-feira'),
        (6, 'Sábado'),
    ]

    profissional = models.ForeignKey(Profissional, on_delete=models.CASCADE, related_name='disponibilidade')
    dia_semana = models.IntegerField(choices=DIAS_DA_SEMANA)
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()

    class Meta:
        unique_together = ('profissional', 'dia_semana', 'hora_inicio', 'hora_fim')

    def __str__(self):
        return f"{self.profissional} - {self.get_dia_semana_display()} ({self.hora_inicio} às {self.hora_fim})"
