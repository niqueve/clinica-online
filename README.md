# Clinica Online

## Sobre
Projeto desenvolvido durante a disciplina de Laboratório Fullstack na Universidade de Vassouras - Maricá-RJ
<br>
Professor: Márcio Garrido

## Resumo
Aplicação Django para gerenciamento de consultas, pacientes e disponibilidade de profissionais. Estrutura modular com apps: `agenda`, `clinica`, `consulta`, `disponibilidade`, `paciente`, `profissional`.

## Tecnologias
- **Python 3.12**, **Django**
- **PostgreSQL** (via Docker)
- **Docker** & **docker-compose**

## Estrutura do projeto 

```text
clinica-online/
    |_ docs/
    |   |_ clinica-online.md # documentacao detalhada
    |   |_ assets # imagens e diagramas gerados
    |
    |_ agenda/
    |   |_ paciente
    |   |_ profissional
    |   |_ consulta
    |   |_ disponibilidade
    |
    |_ README.md # arquivo atual
    |_ Dockerfile
    |_ .gitignore
    |_ .dockerignore
    |_ compose.yaml
    |_ requirements.txt
    |_ requirements-dev.txt # bibliotecas necessárias para rodar testes 
    |_ .env.example # modelo com variaveis de ambiente necessarias

```

## Como utilizar 


1. Copie o modelo de variáveis de ambiente e edite se necessário:

```bash
cp .env.example .env
# editar .env (ex.: POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, DJANGO_SECRET_KEY)
```

2. Suba os serviços (construção + execução em background):

```bash
docker compose up --build -d
```

3. Acesse a aplicação em: http://localhost:8002

4. Criar superuser (se precisar acessar o admin):

```bash
docker compose exec web python agenda/manage.py createsuperuser
```

5. Parar e remover containers, redes e volumes temporários:

```bash
docker compose down --volumes --remove-orphans
```

