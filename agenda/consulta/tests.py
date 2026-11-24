from django.contrib.auth import get_user_model
from django.test import TestCase

from clinica.models import Clinica
from consulta.models import Consulta
from disponibilidade.models import Disponibilidade
from paciente.models import Paciente
from profissional.models import Profissional
from consulta.views import filtrar_consultas_por_organizacao


class ConsultaOrganizacaoTests(TestCase):
    def setUp(self):
        self.usuario_model = get_user_model()

        self.clinica_a = Clinica.objects.create(
            nome='Clínica A',
            cnpj='11.111.111/0001-11',
            rua='Rua A',
            numero='100',
            bairro='Centro',
            cidade='Rio',
            estado='RJ',
            cep='20000-000',
        )
        self.clinica_b = Clinica.objects.create(
            nome='Clínica B',
            cnpj='22.222.222/0001-22',
            rua='Rua B',
            numero='200',
            bairro='Centro',
            cidade='Niterói',
            estado='RJ',
            cep='24000-000',
        )

        self.usuario_paciente = self.usuario_model.objects.create_user(
            username='paciente@clinica.com',
            email='paciente@clinica.com',
            password='123456',
            tipo='PACIENTE',
        )
        self.usuario_profissional = self.usuario_model.objects.create_user(
            username='profissional@clinica.com',
            email='profissional@clinica.com',
            password='123456',
            tipo='PROFISSIONAL',
        )

        self.paciente_a = Paciente.objects.create(
            usuario=self.usuario_paciente,
            clinica=self.clinica_a,
            cpf='111.111.111-11',
            telefone='21999999999',
            data_nascimento='1990-01-01',
            rua='Rua Paciente',
            numero='10',
            bairro='Centro',
            cidade='Rio',
            estado='RJ',
            cep='20000-001',
        )
        self.profissional_a = Profissional.objects.create(
            usuario=self.usuario_profissional,
            clinica=self.clinica_a,
            especialidade='Cardiologia',
            registro_conselho='CRM123456',
            rua='Rua Prof',
            numero='20',
            bairro='Centro',
            cidade='Rio',
            estado='RJ',
            cep='20000-002',
        )

        self.paciente_b = Paciente.objects.create(
            usuario=self.usuario_model.objects.create_user(
                username='paciente2@clinica.com',
                email='paciente2@clinica.com',
                password='123456',
                tipo='PACIENTE',
            ),
            clinica=self.clinica_b,
            cpf='222.222.222-22',
            telefone='21999999998',
            data_nascimento='1985-02-02',
            rua='Rua Paciente 2',
            numero='30',
            bairro='Centro',
            cidade='Niterói',
            estado='RJ',
            cep='24000-001',
        )
        self.profissional_b = Profissional.objects.create(
            usuario=self.usuario_model.objects.create_user(
                username='profissional2@clinica.com',
                email='profissional2@clinica.com',
                password='123456',
                tipo='PROFISSIONAL',
            ),
            clinica=self.clinica_b,
            especialidade='Neurologia',
            registro_conselho='CRM654321',
            rua='Rua Prof 2',
            numero='40',
            bairro='Centro',
            cidade='Niterói',
            estado='RJ',
            cep='24000-002',
        )

        Disponibilidade.objects.create(
            profissional=self.profissional_a,
            dia_semana=4,
            hora_inicio='09:00:00',
            hora_fim='09:30:00',
        )
        Disponibilidade.objects.create(
            profissional=self.profissional_b,
            dia_semana=5,
            hora_inicio='10:00:00',
            hora_fim='10:30:00',
        )

        self.consulta_a = Consulta.objects.create(
            paciente=self.paciente_a,
            profissional=self.profissional_a,
            data_hora_inicio='2026-11-12T09:00:00Z',
            data_hora_fim='2026-11-12T09:30:00Z',
            status='AGENDADA',
        )
        self.consulta_b = Consulta.objects.create(
            paciente=self.paciente_b,
            profissional=self.profissional_b,
            data_hora_inicio='2026-11-13T10:00:00Z',
            data_hora_fim='2026-11-13T10:30:00Z',
            status='AGENDADA',
        )

    def test_paciente_ve_apoenas_consultas_da_sua_clinica(self):
        queryset = filtrar_consultas_por_organizacao(self.usuario_paciente, Consulta.objects.all())
        self.assertEqual(set(queryset.values_list('id', flat=True)), {self.consulta_a.id})

    def test_profissional_ve_apoenas_consultas_da_sua_clinica(self):
        queryset = filtrar_consultas_por_organizacao(self.usuario_profissional, Consulta.objects.all())
        self.assertEqual(set(queryset.values_list('id', flat=True)), {self.consulta_a.id})
