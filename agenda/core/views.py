from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from datetime import datetime, timedelta

from consulta.models import Consulta
from consulta.views import filtrar_consultas_por_organizacao
from paciente.models import Paciente
from profissional.models import Profissional
from clinica.models import Clinica
from .forms import UsuarioPerfilForm, PacientePerfilForm
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from .models import Usuario


class CustomLoginView(LoginView):
    template_name = 'core/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('core:dashboard')


@login_required
def dashboard_view(request):
    user = request.user
    context = {}

    sincronizar_tipo_por_perfil(user)

    if not user.tipo:
        return redirect('core:selecionar_perfil')

    if user.tipo in ['PROFISSIONAL', 'CLINICA'] and user.status_aprovacao != 'APROVADO':
        return render(request, 'core/aguardando_aprovacao.html')

    if user.is_superuser or (hasattr(user, 'tipo') and user.tipo == 'ADMIN'):
        context['total_consultas'] = Consulta.objects.count()
        context['total_pacientes'] = Paciente.objects.count()
        context['total_profissionais'] = Profissional.objects.count()
        context['total_clinicas'] = Clinica.objects.count()
        context['usuarios_pendentes'] = Usuario.objects.filter(
            status_aprovacao='PENDENTE',
            profissional__isnull=False,
        ).select_related('profissional')
        template_name = 'core/dashboard_admin.html'

    elif user.tipo == 'PROFISSIONAL':
        profissional = Profissional.objects.filter(usuario=user).first()
        queryset = Consulta.objects.filter(profissional=profissional) if profissional else Consulta.objects.none()
        context['consultas'] = queryset.order_by('-data_hora_inicio')
        context['profissional'] = profissional
        context['pacientes'] = Paciente.objects.filter(clinica=profissional.clinica) if profissional and profissional.clinica else Paciente.objects.none()
        context['consultas_agendadas'] = queryset.filter(status='AGENDADA').count()
        template_name = 'core/dashboard_profissional.html'

    else:
        paciente = Paciente.objects.filter(usuario=user).first()
        if paciente:
            queryset = Consulta.objects.filter(paciente=paciente)
            clinicas = Clinica.objects.all()
            profissionais = Profissional.objects.filter(clinica=paciente.clinica) if paciente.clinica else Profissional.objects.none()
        else:
            queryset = Consulta.objects.none()
            clinicas = Clinica.objects.all()
            profissionais = Profissional.objects.none()

        context['paciente'] = paciente
        context['consultas'] = queryset.order_by('-data_hora_inicio')
        context['consultas_agendadas'] = queryset.filter(status='AGENDADA')
        context['historico_consultas'] = queryset.exclude(status='AGENDADA').order_by('-data_hora_inicio')
        context['clinicas'] = clinicas
        context['profissionais'] = profissionais
        context['solicitacao_profissional_pendente'] = (
            user.status_aprovacao == 'PENDENTE'
            and Profissional.objects.filter(usuario=user).exists()
        )
        template_name = 'core/dashboard_paciente.html'

    return render(request, template_name, context)

def home_view(request):
    return render(request, 'core/home.html')

class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = (request.data.get('email') or '').strip().lower()
        password = request.data.get('password') or ''
        name = (request.data.get('name') or '').strip()

        if not email or not password:
            return Response({'error': 'E-mail e senha são obrigatórios.'}, status=status.HTTP_400_BAD_REQUEST)

        if Usuario.objects.filter(email__iexact=email).exists():
            return Response({'error': 'Este e-mail já está cadastrado.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password(password)
        except ValidationError as exc:
            return Response({'error': exc.messages[0]}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = Usuario.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name,
                tipo='PACIENTE',
                status_aprovacao='APROVADO'
            )

            Paciente.objects.create(
                usuario=user,
                rua='', numero='', bairro='', cidade='', estado='', cep='',
            )

            token, _ = Token.objects.get_or_create(user=user)
            auth_login(request, user)

            return Response({
                'message': 'Usuário cadastrado como paciente com sucesso!',
                'token': token.key,
                'redirect_url': reverse('core:dashboard')
            }, status=status.HTTP_201_CREATED)

        except Exception as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

def selecionar_perfil_view(request):
    if request.user.is_authenticated:
        sincronizar_tipo_por_perfil(request.user)
        if request.user.tipo:
            return redirect('core:dashboard')

    if request.method == 'POST':
        tipo_escolhido = request.POST.get('tipo')

        if request.user.is_authenticated:
            user = request.user
        else:
            user = Usuario.objects.filter(status_aprovacao='PENDENTE').last()

        if user:
            user.tipo = tipo_escolhido
            if tipo_escolhido == 'PACIENTE':
                user.status_aprovacao = 'APROVADO'
                user.save()
                
                auth_login(request, user)
                
                return redirect('/dashboard/')
            else:
                user.status_aprovacao = 'PENDENTE'
                user.save()
                return render(request, 'core/aguardando_aprovacao.html')

    return render(request, 'core/selecionar_perfil.html')

class SessionLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            sincronizar_tipo_por_perfil(user)
            return Response({'message': 'Login realizado com sucesso!', 'redirect_url': '/dashboard/'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'E-mail ou senha inválidos.'}, status=status.HTTP_400_BAD_REQUEST)

@login_required
def editar_perfil_view(request):
    paciente = Paciente.objects.filter(usuario=request.user).first()
    if request.user.tipo != 'PACIENTE' or not paciente:
        messages.error(request, 'Esta área é disponível apenas para pacientes cadastrados.')
        return redirect('core:dashboard')

    if request.method == 'POST':
        usuario_form = UsuarioPerfilForm(request.POST, instance=request.user)
        paciente_form = PacientePerfilForm(request.POST, instance=paciente)
        if usuario_form.is_valid() and paciente_form.is_valid():
            usuario_form.save()
            paciente_form.save()
            messages.success(request, 'Dados pessoais atualizados com sucesso.')
            return redirect('core:editar_perfil')
    else:
        usuario_form = UsuarioPerfilForm(instance=request.user)
        paciente_form = PacientePerfilForm(instance=paciente)

    return render(request, 'core/editar_perfil.html', {
        'usuario_form': usuario_form,
        'paciente_form': paciente_form,
    })

@login_required
def agendar_consulta_view(request):
    if request.method != 'POST':
        return redirect('core:dashboard')

    profissional = get_object_or_404(Profissional, pk=request.POST.get('profissional'))

    if request.user.tipo == 'PACIENTE':
        paciente = get_object_or_404(Paciente, usuario=request.user)
        if paciente.clinica_id and profissional.clinica_id != paciente.clinica_id:
            messages.error(request, 'Selecione um profissional da sua clínica.')
            return redirect('core:dashboard')
    elif request.user.tipo == 'PROFISSIONAL':
        profissional_logado = Profissional.objects.filter(usuario=request.user).first()
        if not profissional_logado or profissional.id != profissional_logado.id:
            messages.error(request, 'Você só pode agendar consultas para si mesmo.')
            return redirect('core:dashboard')
        paciente = get_object_or_404(Paciente, pk=request.POST.get('paciente'))
        if profissional_logado.clinica_id != paciente.clinica_id:
            messages.error(request, 'O paciente não pertence à sua clínica.')
            return redirect('core:dashboard')
    else:
        messages.error(request, 'Você não tem permissão para agendar consultas.')
        return redirect('core:dashboard')

    try:
        inicio = datetime.fromisoformat(request.POST.get('data_hora_inicio', '').replace('Z', '+00:00'))
        inicio = timezone.make_aware(inicio) if timezone.is_naive(inicio) else inicio

        if inicio < timezone.now():
            messages.error(request, 'A data e hora da consulta não podem estar no passado.')
            return redirect('core:dashboard')

        fim = inicio + timedelta(minutes=30)
        consulta = Consulta(
            paciente=paciente,
            profissional=profissional,
            data_hora_inicio=inicio,
            data_hora_fim=fim,
            observacoes=request.POST.get('observacoes', '').strip(),
            status='AGENDADA',
        )
        consulta.save()
        messages.success(request, 'Consulta agendada com sucesso.')
    except (ValidationError, ValueError, TypeError) as exc:
        if hasattr(exc, 'messages'):
            messages.error(request, ' '.join(exc.messages))
        else:
            messages.error(request, str(exc))

    return redirect('core:dashboard')


@login_required
def cancelar_consulta_view(request, consulta_id):
    consulta = get_object_or_404(Consulta, pk=consulta_id)

    if request.user.tipo == 'PACIENTE':
        paciente = Paciente.objects.filter(usuario=request.user).first()
        permitido = paciente and consulta.paciente_id == paciente.id
    elif request.user.tipo == 'PROFISSIONAL':
        profissional = Profissional.objects.filter(usuario=request.user).first()
        permitido = profissional and consulta.profissional_id == profissional.id
    else:
        permitido = request.user.is_superuser or request.user.tipo == 'ADMIN'

    if not permitido:
        messages.error(request, 'Você não tem permissão para cancelar esta consulta.')
        return redirect('core:dashboard')

    if consulta.status == 'AGENDADA':
        consulta.status = 'CANCELADA'
        consulta.save(update_fields=['status'])
        messages.success(request, 'Consulta cancelada com sucesso.')
    else:
        messages.warning(request, 'Esta consulta já não está agendada.')

    return redirect('core:dashboard')

@login_required
def relatorio_consultas_view(request):
    user = request.user
    consultas = Consulta.objects.none()

    if user.tipo == 'PACIENTE':
        paciente = Paciente.objects.filter(usuario=user).first()
        consultas = Consulta.objects.filter(paciente=paciente).order_by('-data_hora')
    elif user.tipo == 'PROFISSIONAL':
        profissional = Profissional.objects.filter(usuario=user).first()
        consultas = Consulta.objects.filter(profissional=profissional).order_by('-data_hora')
    elif user.is_superuser or (hasattr(user, 'tipo') and user.tipo == 'ADMIN'):
        consultas = Consulta.objects.all().order_by('-data_hora')

    # Filtrar consultas por data
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')

    if data_inicio and data_fim:
        try:
            data_inicio = timezone.datetime.strptime(data_inicio, '%Y-%m-%d')
            data_fim = timezone.datetime.strptime(data_fim, '%Y-%m-%d') + timedelta(days=1)

            consultas = consultas.filter(data_hora__range=(data_inicio, data_fim))
        except ValueError:
            messages.error(request, 'Formato de data inválido. Use AAAA-MM-DD.')

    return render(request, 'core/relatorio_consultas.html', {'consultas': consultas})

def sincronizar_tipo_por_perfil(user):
    """Sincroniza tipos criados pelo painel sem alterar solicitações profissionais pendentes."""
    if user.is_superuser:
        if user.tipo != 'ADMIN':
            user.tipo = 'ADMIN'
            user.status_aprovacao = 'APROVADO'
            user.save(update_fields=['tipo', 'status_aprovacao'])
        return user.tipo

    if user.tipo == 'PACIENTE':
        if not Paciente.objects.filter(usuario=user).exists():
            Paciente.objects.create(
                usuario=user, rua='', numero='', bairro='', cidade='', estado='', cep='',
            )

        if user.status_aprovacao == 'APROVADO' and Profissional.objects.filter(usuario=user).exists():
            user.tipo = 'PROFISSIONAL'
            user.save(update_fields=['tipo'])

        return user.tipo

    if user.status_aprovacao == 'APROVADO' and Profissional.objects.filter(usuario=user).exists():
        if user.tipo != 'PROFISSIONAL':
            user.tipo = 'PROFISSIONAL'
            user.save(update_fields=['tipo'])
        return user.tipo

    if Paciente.objects.filter(usuario=user).exists():
        user.tipo = 'PACIENTE'
        user.status_aprovacao = 'APROVADO'
        user.save(update_fields=['tipo', 'status_aprovacao'])

    elif Profissional.objects.filter(usuario=user).exists():
        user.tipo = 'PROFISSIONAL'
        user.save(update_fields=['tipo'])

    return user.tipo

@login_required
def solicitar_profissional_view(request):
    if request.user.tipo != 'PACIENTE':
        messages.warning(request, 'Esta solicitação está disponível apenas para contas de paciente.')
        return redirect('core:dashboard')

    if request.method == 'POST':
        clinica = Clinica.objects.filter(pk=request.POST.get('clinica')).first()
        especialidade = (request.POST.get('especialidade') or '').strip()
        registro = (request.POST.get('registro_conselho') or '').strip()

        if not clinica or not especialidade:
            messages.error(request, 'Selecione uma clínica e informe sua especialidade.')
            return redirect('core:dashboard')

        paciente = Paciente.objects.filter(usuario=request.user).first()

        Profissional.objects.update_or_create(
            usuario=request.user,
            defaults={
                'clinica': clinica,
                'especialidade': especialidade,
                'registro_conselho': registro or None,
                'rua': paciente.rua if paciente else '',
                'numero': paciente.numero if paciente else '',
                'bairro': paciente.bairro if paciente else '',
                'cidade': paciente.cidade if paciente else '',
                'estado': paciente.estado if paciente else '',
                'cep': paciente.cep if paciente else '',
            },
        )

        request.user.status_aprovacao = 'PENDENTE'
        request.user.save(update_fields=['status_aprovacao'])

        messages.success(request, 'Solicitação enviada. Aguarde a aprovação da administração.')
        return redirect('core:dashboard')

    solicitacao_pendente = (
        request.user.status_aprovacao == 'PENDENTE'
        and Profissional.objects.filter(usuario=request.user).exists()
    )

    profissional = Profissional.objects.filter(usuario=request.user).first()
    return render(request, 'core/solicitar_profissional.html', {
        'clinicas': Clinica.objects.all(),
        'solicitacao_pendente': solicitacao_pendente,
        'profissional': profissional,
    })

@login_required
def aprovar_profissional_view(request, usuario_id):
    if not (request.user.is_superuser or request.user.tipo == 'ADMIN'):
        messages.error(request, 'Apenas administradores podem aprovar solicitações.')
        return redirect('core:dashboard')

    usuario = get_object_or_404(Usuario, pk=usuario_id)
    if request.method == 'POST' and Profissional.objects.filter(usuario=usuario).exists():
        usuario.status_aprovacao = 'APROVADO'
        usuario.tipo = 'PROFISSIONAL'
        usuario.save(update_fields=['status_aprovacao', 'tipo'])
        messages.success(request, 'Cadastro profissional aprovado.')

    return redirect('core:dashboard')


@login_required
def rejeitar_profissional_view(request, usuario_id):
    if not (request.user.is_superuser or request.user.tipo == 'ADMIN'):
        messages.error(request, 'Apenas administradores podem rejeitar solicitações.')
        return redirect('core:dashboard')

    usuario = get_object_or_404(Usuario, pk=usuario_id)
    if request.method == 'POST':
        usuario.status_aprovacao = 'REJEITADO'
        usuario.tipo = 'PACIENTE'
        usuario.save(update_fields=['status_aprovacao', 'tipo'])
        Profissional.objects.filter(usuario=usuario).delete()
        messages.success(request, 'Solicitação profissional rejeitada.')

    return redirect('core:dashboard')