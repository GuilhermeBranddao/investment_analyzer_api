

### Instalando dependencias
python -m venv .venv

G:/py_projects/investment_analyzer_api/.venv/Scripts/activate.bat

pip install -r requirements.txt

### Rode os testes
pytest


### Rodando API
uvicorn app.main:app --reload

Visite o link abaixo para visualizar a documentação da api
http://127.0.0.1:8000/docs

### Como trabalhar com alembic

Passo 1: Atualizar base de dados
- alembic revision --autogenerate -m "initial migration"
- alembic upgrade head


Passo 2: rodar etl
- task run_etl# Finalyzer
