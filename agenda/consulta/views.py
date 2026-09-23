from django.shortcuts import render
from .models import Consulta

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