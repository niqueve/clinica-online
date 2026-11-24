from django.test import TestCase
from django.urls import reverse

from core.models import Usuario
from clinica.models import Clinica
from profissional.models import Profissional


class CadastroUsuarioTests(TestCase):
    def test_registro_cria_usuario_como_paciente_aprovado(self):
        payload = {
            'name': 'Ana Souza',
            'email': 'ana@example.com',
            'password': 'Senha@123'
        }

        response = self.client.post(
            reverse('core:api_register'),
            payload,
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)
        usuario = Usuario.objects.get(email='ana@example.com')
        self.assertEqual(usuario.tipo, 'PACIENTE')
        self.assertEqual(usuario.status_aprovacao, 'APROVADO')
        self.assertTrue(hasattr(usuario, 'paciente'))
        self.assertEqual(response.json()['redirect_url'], reverse('core:dashboard'))

    def test_registro_rejeita_senha_vazia(self):
        payload = {
            'name': 'Ana Souza',
            'email': 'ana@example.com',
            'password': ''
        }

        response = self.client.post(
            reverse('core:api_register'),
            payload,
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)

    def test_profissional_cadastrado_redireciona_para_dashboard(self):
        clinica = Clinica.objects.create(
            nome='Clínica Teste', cnpj='99.999.999/0001-99',
            rua='Rua', numero='1', bairro='Centro', cidade='Cidade',
            estado='SP', cep='00000-000',
        )
        usuario = Usuario.objects.create_user(
            username='profissional@teste.com',
            email='profissional@teste.com',
            password='Senha@123',
            tipo=None,
            status_aprovacao='APROVADO',
        )
        Profissional.objects.create(
            usuario=usuario, clinica=clinica, especialidade='Cardiologia',
            registro_conselho='CRM-TESTE', rua='Rua', numero='2', bairro='Centro',
            cidade='Cidade', estado='SP', cep='00000-001',
        )

        login = self.client.login(username=usuario.username, password='Senha@123')
        self.assertTrue(login)

        response = self.client.get(reverse('core:dashboard'))

        usuario.refresh_from_db()
        self.assertEqual(usuario.tipo, 'PROFISSIONAL')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/dashboard_profissional.html')

    def test_paciente_solicita_profissional_sem_perder_acesso_paciente(self):
        clinica = Clinica.objects.create(
            nome='Clínica Solicitação', cnpj='88.888.888/0001-88',
            rua='Rua', numero='1', bairro='Centro', cidade='Cidade',
            estado='SP', cep='00000-000',
        )
        usuario = Usuario.objects.create_user(
            username='paciente@teste.com', email='paciente@teste.com',
            password='Senha@123', tipo='PACIENTE', status_aprovacao='APROVADO',
        )
        usuario.paciente if hasattr(usuario, 'paciente') else None

        from paciente.models import Paciente
        Paciente.objects.create(
            usuario=usuario, rua='Rua', numero='1', bairro='Centro',
            cidade='Cidade', estado='SP', cep='00000-000',
        )

        self.client.login(username=usuario.username, password='Senha@123')
        response = self.client.post(reverse('core:solicitar_profissional'), {
            'clinica': clinica.id,
            'especialidade': 'Dermatologia',
            'registro_conselho': 'CRM-123',
        })

        usuario.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(usuario.tipo, 'PACIENTE')
        self.assertEqual(usuario.status_aprovacao, 'PENDENTE')
        self.assertTrue(Profissional.objects.filter(usuario=usuario).exists())
