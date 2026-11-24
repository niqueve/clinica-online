from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from disponibilidade.models import Disponibilidade
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

    def clean(self):
        super().clean()

        if self.data_hora_inicio and self.data_hora_fim:
            if self.data_hora_inicio >= self.data_hora_fim:
                raise ValidationError('A data/hora de término deve ser posterior à data/hora de início.')

            dia_semana = (self.data_hora_inicio.weekday() + 1) % 7
            hora_inicio_consulta = timezone.localtime(self.data_hora_inicio).time()
            hora_fim_consulta = timezone.localtime(self.data_hora_fim).time()

            disponivel = Disponibilidade.objects.filter(
                profissional=self.profissional,
                dia_semana=dia_semana,
                hora_inicio__lte=hora_inicio_consulta,
                hora_fim__gte=hora_fim_consulta,
            ).exists()

            if not disponivel:
                raise ValidationError('O profissional não atende neste dia ou horário.')

            conflitos = Consulta.objects.filter(
                profissional=self.profissional,
                status='AGENDADA',
                data_hora_inicio__lt=self.data_hora_fim,
                data_hora_fim__gt=self.data_hora_inicio,
            )

            if self.pk:
                conflitos = conflitos.exclude(pk=self.pk)

            if conflitos.exists():
                raise ValidationError('O profissional já possui uma consulta agendada para este horário')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Consulta: {self.paciente} com {self.profissional} em {self.data_hora_inicio.strftime('%d/%m/%Y %H:%M')}"
