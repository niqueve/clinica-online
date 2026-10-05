from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from core.serializers import PacienteSerializer
from paciente.models import Paciente

class PacienteViewSet(viewsets.ModelViewSet):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Paciente.objects.all()

        if hasattr(user, 'tipo') and user.tipo == 'PACIENTE':
            return queryset.filter(usuario=user)

        clinica_id = self.request.query_params.get('clinica')
        if clinica_id:
            queryset = queryset.filter(clinica_id=clinica_id)

        return queryset
