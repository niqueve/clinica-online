from django import forms
from django.utils import timezone
from .models import Consulta

class ConsultaModelForm(forms.ModelForm):
    class Meta:
        model = Consulta
        fields = ['paciente', 'profissional', 'data_hora_inicio', 'data_hora_fim', 'observacoes']
        widgets = {
            'data_hora_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'data_hora_fim': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'paciente': forms.Select(attrs={'class': 'form-control'}),
            'profissional': forms.Select(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_data_hora_inicio(self):
        data_inicio = self.cleaned_data.get('data_hora_inicio')
        
        # Feature 2: A data da consulta não pode estar no passado
        if data_inicio and data_inicio < timezone.now():
            raise forms.ValidationError("A data e hora da consulta não podem estar no passado.")
        
        return data_inicio

    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_hora_inicio')
        data_fim = cleaned_data.get('data_hora_fim')

        if data_inicio and data_fim and data_inicio >= data_fim:
            raise forms.ValidationError("A data/hora de término deve ser posterior à data/hora de início.")

        return cleaned_data