# Usar a imagem base do Python 3.12
FROM python:3.12-slim

# Definir diretório de trabalho dentro do contêiner
WORKDIR /app

# Instalar dependências do sistema para o Poetry (se necessário, por exemplo, para compilar dependências)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar o arquivo de configuração do Poetry e o pyproject.toml para o contêiner
COPY pyproject.toml poetry.lock /app/

# Instalar o Poetry
RUN pip install poetry

# Instalar as dependências do projeto utilizando Poetry
RUN poetry install --no-interaction --no-root

# Copiar o restante dos arquivos do projeto
COPY . /app

# Definir variável de ambiente para o Python
ENV PYTHONPATH=/app

# Expor a porta do servidor (ajuste conforme necessário)
EXPOSE 8000

# Definir o comando padrão para rodar o seu servidor (UVicorn)
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
