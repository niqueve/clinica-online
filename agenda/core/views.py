from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from consulta.models import Consulta
from paciente.models import Paciente
from profissional.models import Profissional
from clinica.models import Clinica
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

    if not user.tipo:
        return redirect('core:selecionar_perfil')

    if user.tipo in ['PROFISSIONAL', 'CLINICA'] and user.status_aprovacao != 'APROVADO':
        return render(request, 'core/aguardando_aprovacao.html')

    if user.is_superuser or (hasattr(user, 'tipo') and user.tipo == 'ADMIN'):
        context['total_consultas'] = Consulta.objects.count()
        context['total_pacientes'] = Paciente.objects.count()
        context['total_profissionais'] = Profissional.objects.count()
        context['total_clinicas'] = Clinica.objects.count()
        template_name = 'core/dashboard_admin.html'

    elif hasattr(user, 'tipo') and user.tipo == 'PROFISSIONAL':
        profissional = Profissional.objects.filter(usuario=user).first()
        context['consultas'] = Consulta.objects.filter(profissional=profissional) if profissional else []
        template_name = 'core/dashboard_profissional.html'

    else:
        paciente = Paciente.objects.filter(usuario=user).first()
        context['consultas'] = Consulta.objects.filter(paciente=paciente) if paciente else []
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
                status_aprovacao='PENDENTE'
            )

            token, _ = Token.objects.get_or_create(user=user)

            return Response({
                'message': 'Usuário cadastrado com sucesso!',
                'token': token.key,
                'redirect_url': reverse('core:selecionar_perfil')
            }, status=status.HTTP_201_CREATED)

        except Exception as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

def selecionar_perfil_view(request):
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
            return Response({'message': 'Login realizado com sucesso!', 'redirect_url': '/dashboard/'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'E-mail ou senha inválidos.'}, status=status.HTTP_400_BAD_REQUEST)