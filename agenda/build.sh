#!/usr/bin/env bash
# Encerrar em caso de erro
set -o errexit

# Instalar dependências
pip install -r requirements.txt

# Coletar arquivos estáticos
python manage.py collectstatic --no-input

# Rodar as migrações no banco de dados do Supabase
python manage.py migrate