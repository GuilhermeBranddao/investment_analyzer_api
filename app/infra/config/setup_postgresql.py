import os
import subprocess
import psycopg2
from psycopg2 import sql
from app.settings.config import Settings

settings = Settings()

ENV_PATH = ".env"

def run_command(command):
    """Executa um comando no terminal e captura a saída."""
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar o comando: {e}")
        exit(1)

def setup_postgresql():
    """Configura o PostgreSQL no sistema."""
    print("Configurando PostgreSQL...")

    # Instala o PostgreSQL (dependendo do sistema operacional)
    print("Instalando PostgreSQL...")
    run_command("sudo apt update && sudo apt install -y postgresql postgresql-contrib")

    # Inicia o serviço PostgreSQL
    print("Iniciando o serviço PostgreSQL...")
    run_command("sudo systemctl start postgresql")
    run_command("sudo systemctl enable postgresql")

def configure_database():
    """Cria o banco de dados e o usuário no PostgreSQL."""
    try:
        print("Conectando ao PostgreSQL...")
        connection = psycopg2.connect(
            dbname="postgres",
            user="postgres",  # Usuário padrão
            password="",      # Pode ser necessário ajustar
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT
        )
        connection.autocommit = True
        cursor = connection.cursor()

        # Cria o usuário e o banco de dados, se não existirem
        print("Criando o usuário e o banco de dados...")
        cursor.execute(
            sql.SQL("CREATE USER {user} WITH PASSWORD %s").format(user=sql.Identifier(settings.POSTGRES_USER)),
            [settings.POSTGRES_PASSWORD]
        )
        cursor.execute(
            sql.SQL("CREATE DATABASE {db} OWNER {user}").format(
                db=sql.Identifier(settings.POSTGRES_DB),
                user=sql.Identifier(settings.POSTGRES_USER)
            )
        )
        cursor.execute(
            sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {db} TO {user}").format(
                db=sql.Identifier(settings.POSTGRES_DB),
                user=sql.Identifier(settings.POSTGRES_USER)
            )
        )
        print("Banco de dados e usuário criados com sucesso!")
    except Exception as e:
        print(f"Erro ao configurar banco de dados: {e}")
    finally:
        if connection:
            connection.close()

def update_pg_hba_conf():
    """Atualiza o arquivo pg_hba.conf para autenticação correta."""
    print("Atualizando o arquivo pg_hba.conf...")
    pg_hba_path = "/etc/postgresql/<versão>/main/pg_hba.conf"  # Ajuste o caminho se necessário
    try:
        # Faz backup do arquivo original
        run_command(f"sudo cp {pg_hba_path} {pg_hba_path}.backup")

        # Atualiza as regras de autenticação
        with open(pg_hba_path, "a") as pg_hba:
            pg_hba.write("\n# Regra para conexão local do usuário\n")
            pg_hba.write("host    all             all             127.0.0.1/32            md5\n")
        print("Arquivo pg_hba.conf atualizado com sucesso!")

        # Reinicia o serviço PostgreSQL
        print("Reiniciando o PostgreSQL...")
        run_command("sudo systemctl restart postgresql")
    except Exception as e:
        print(f"Erro ao atualizar o arquivo pg_hba.conf: {e}")
        exit(1)

def update_env_file():
    """Atualiza o arquivo .env com os dados do banco PostgreSQL."""
    print("Atualizando o arquivo .env...")
    try:
        with open(ENV_PATH, "w") as env_file:
            env_file.write(f"DATABASE_URL=postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}\n")
        print(f"Arquivo {ENV_PATH} atualizado com sucesso!")
    except Exception as e:
        print(f"Erro ao atualizar o arquivo .env: {e}")
        exit(1)

def main():
    print("Iniciando automação do PostgreSQL...")
    
    # 1. Configura o PostgreSQL
    setup_postgresql()

    # 2. Cria o banco de dados e o usuário
    configure_database()

    # 3. Atualiza o pg_hba.conf
    update_pg_hba_conf()

    # 4. Atualiza o arquivo .env
    update_env_file()

    print("Automação concluída com sucesso!")

if __name__ == "__main__":
    main()
