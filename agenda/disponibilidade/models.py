from django.db import models
from django.core.exceptions import ValidationError
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

    def clean(self):
        super().clean()

        if self.hora_inicio and self.hora_fim and self.hora_inicio >= self.hora_fim:
            raise ValidationError('O horário de início deve ser anterior ao horário de fim.')

        sobreposicoes = Disponibilidade.objects.filter(
            profissional=self.profissional,
            dia_semana=self.dia_semana,
            hora_inicio__lt=self.hora_fim,
            hora_fim__gt=self.hora_inicio,
        )
        if self.pk:
            sobreposicoes = sobreposicoes.exclude(pk=self.pk)

        if sobreposicoes.exists():
            raise ValidationError('Já existe um horário cadastrado que sobrepõe o intervalo informado.')

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.profissional} - {self.get_dia_semana_display()} ({self.hora_inicio} às {self.hora_fim})"
