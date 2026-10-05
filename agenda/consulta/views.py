from django.shortcuts import render
from .models import Consulta
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from core.serializers import ConsultaSerializer
from consulta.models import Consulta

class ConsultaViewSet(viewsets.ModelViewSet):
    queryset = Consulta.objects.all()
    serializer_class = ConsultaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Consulta.objects.all()

        #------------------------------------------- Isolamento de consultas por papel do usuario
        if hasattr(user, 'tipo'):
            if user.tipo == 'PACIENTE':
                queryset = queryset.filter(paciente__usuario=user)
            elif user.tipo == 'PROFISSIONAL':
                queryset = queryset.filter(profissional__usuario=user)

        #------------------------------------------------ Filtro de multiplas clínicas por parâmetro na URL 
        clinica_id = self.request.query_params.get('clinica')
        if clinica_id:
            queryset = queryset.filter(paciente__clinica_id=clinica_id)

        return queryset

def lista_consultas(request):
    termo_busca = request.GET.get('q', '')
    especialidade_filtro = request.GET.get('especialidade', '')

    consultas = Consulta.objects.all()

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

    from profissional.models import Profissional
    especialidades = Profissional.objects.values_list('especialidade', flat=True).distinct()

    context = {
        'consultas': consultas,
        'termo_busca': termo_busca,
        'especialidade_filtro': especialidade_filtro,
        'especialidades': especialidades,
    }
    return render(request, 'consulta/lista_consultas.html', context)