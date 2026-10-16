from django.test import TestCase
from django.urls import reverse

from core.models import Usuario


class CadastroUsuarioTests(TestCase):
    def test_registro_cria_usuario_e_redireciona_para_selecao_de_perfil(self):
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
        self.assertTrue(Usuario.objects.filter(email='ana@example.com').exists())
        self.assertEqual(response.json()['redirect_url'], reverse('core:selecionar_perfil'))

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
