from django.db.models import Q
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from clinica.models import Clinica
from core.serializers import ConsultaSerializer
from paciente.models import Paciente
from profissional.models import Profissional
from .models import Consulta


def filtrar_consultas_por_organizacao(user, queryset=None, clinica_id=None):
    queryset = queryset if queryset is not None else Consulta.objects.all()

    if not getattr(user, 'is_authenticated', False):
        return queryset

    if getattr(user, 'tipo', None) == 'ADMIN':
        return queryset

    if clinica_id:
        return queryset.filter(
            Q(paciente__clinica_id=clinica_id) | Q(profissional__clinica_id=clinica_id)
        )

    if getattr(user, 'tipo', None) == 'PACIENTE':
        paciente = Paciente.objects.filter(usuario=user).first()
        if not paciente or not paciente.clinica_id:
            return queryset.none()
        return queryset.filter(
            Q(paciente__clinica_id=paciente.clinica_id) |
            Q(profissional__clinica_id=paciente.clinica_id)
        )

    if getattr(user, 'tipo', None) == 'PROFISSIONAL':
        profissional = Profissional.objects.filter(usuario=user).first()
        if not profissional or not profissional.clinica_id:
            return queryset.none()
        return queryset.filter(
            Q(paciente__clinica_id=profissional.clinica_id) |
            Q(profissional__clinica_id=profissional.clinica_id)
        )

    if getattr(user, 'tipo', None) == 'CLINICA':
        return queryset.none()

    return queryset


class ConsultaViewSet(viewsets.ModelViewSet):
    queryset = Consulta.objects.all()
    serializer_class = ConsultaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Consulta.objects.all()

        clinica_id = self.request.query_params.get('clinica')
        return filtrar_consultas_por_organizacao(user, queryset, clinica_id)


def lista_consultas(request):
    termo_busca = request.GET.get('q', '')
    especialidade_filtro = request.GET.get('especialidade', '')
    clinica_filtro = request.GET.get('clinica', '')

    consultas = Consulta.objects.all()
    consultas = filtrar_consultas_por_organizacao(request.user, consultas, clinica_filtro)

    #---------------------------------------------------------------- Busca por texto no nome do paciente (ou nome do usuário associado)
    if termo_busca:
        consultas = consultas.filter(
            paciente__usuario__first_name__icontains=termo_busca
        ) | consultas.filter(
            paciente__usuario__username__icontains=termo_busca
        )

    #--------------------------------------------------------------- Busca por especialidade
    if especialidade_filtro:
        consultas = consultas.filter(
            profissional__especialidade__icontains=especialidade_filtro
        )

    if clinica_filtro:
        consultas = consultas.filter(
            Q(paciente__clinica_id=clinica_filtro) | Q(profissional__clinica_id=clinica_filtro)
        )

    especialidades = Profissional.objects.values_list('especialidade', flat=True).distinct()
    clinicas = Clinica.objects.all()

    context = {
        'consultas': consultas,
        'termo_busca': termo_busca,
        'especialidade_filtro': especialidade_filtro,
        'clinica_filtro': clinica_filtro,
        'especialidades': especialidades,
        'clinicas': clinicas,
    }
    return render(request, 'consulta/lista_consultas.html', context)