from django import forms

from core.models import Usuario
from paciente.models import Paciente


class UsuarioPerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['first_name', 'email', 'username']
        labels = {
            'first_name': 'Nome completo',
            'email': 'E-mail',
            'username': 'Nome de usuário',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }


class PacientePerfilForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = [
            'clinica', 'cpf', 'telefone', 'data_nascimento',
            'rua', 'numero', 'bairro', 'cidade', 'estado', 'cep',
        ]
        labels = {
            'clinica': 'Clínica',
            'cpf': 'CPF',
            'telefone': 'Telefone',
            'data_nascimento': 'Data de nascimento',
            'rua': 'Rua',
            'numero': 'Número',
            'bairro': 'Bairro',
            'cidade': 'Cidade',
            'estado': 'Estado',
            'cep': 'CEP',
        }
        widgets = {
            'clinica': forms.Select(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'data_nascimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'rua': forms.TextInput(attrs={'class': 'form-control'}),
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '2'}),
            'cep': forms.TextInput(attrs={'class': 'form-control'}),
        }
