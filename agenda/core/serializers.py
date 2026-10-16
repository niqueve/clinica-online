from rest_framework import serializers
from clinica.models import Clinica
from paciente.models import Paciente
from profissional.models import Profissional
from disponibilidade.models import Disponibilidade
from consulta.models import Consulta

class ClinicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinica
        fields = '__all__'

class PacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = '__all__'

class ProfissionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profissional
        fields = '__all__'

class DisponibilidadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disponibilidade
        fields = '__all__'

class ConsultaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consulta
        fields = '__all__'
