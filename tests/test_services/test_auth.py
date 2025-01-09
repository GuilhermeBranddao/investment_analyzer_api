import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.infra.config.database import Base, create_engine_db, get_db, create_all_tables
from app.main import app
from app.settings.config import Settings
from app.validation.email_validation import validate_email
from app.validation.name_validation import validate_name
from app.validation.password_validation import validate_password
from app.repository.auth import RepositoryUser
from app.models.models import *
from fastapi import HTTPException

settings = Settings()

# Configuração do banco de dados para testes
engine = create_engine_db(settings.DATABASE_TEST_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

create_all_tables(engine=engine, Base=Base)
# Criando o banco de dados
#Base.metadata.create_all(bind=engine)

# Fixtures
@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session  # Disponibiliza a sessão para os testes

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture
def repository_user(db_session):
    return RepositoryUser(db_session)


# Função helper para criar usuários
def create_user(client, name, email, password):
    payload = {"name": name, "email": email, "password": password}
    return client.post("/auth/signup", json=payload)


# Testes de criação de usuários
def test_create_user_successfully(client, repository_user):
    payload = {"name": "John Doe", "password": "#1234Abcd", "email": "johndoe@example.com"}
    
    response = create_user(client, **payload)
    data = response.json()

    assert response.status_code == 200, "Falha ao criar o usuário com sucesso"
    assert data["name"] == payload["name"], "O nome retornado não coincide"
    assert data["email"] == payload["email"], "O e-mail retornado não coincide"
    assert "id" in data, "ID do usuário não foi retornado"

    user_from_db = repository_user.get_user_per_email(payload["email"])
    assert user_from_db is not None, "Usuário não foi encontrado no banco de dados"
    assert user_from_db.email == payload["email"], "O e-mail do usuário no banco não coincide"


def test_create_two_equal_users(client):
    payload = {"name": "Jane Doe", "password": "#1234Abcd", "email": "janedoe@example.com"}

    response1 = create_user(client, **payload)
    response2 = create_user(client, **payload)

    assert response1.status_code == 200, "Falha ao criar o primeiro usuário"
    assert response2.status_code == 400, "Não deveria ser possível criar dois usuários com o mesmo e-mail"
    assert response2.json()["detail"] == "Já existe um usuário registrado com este e-mail."


# Valid name
def test_valid_name():
    assert validate_name("John Doe") is True, "Nome válido não foi aceito"


def test_name_too_short():
    with pytest.raises(HTTPException) as exc_info:
        validate_name("Jo")
    assert exc_info.value.status_code == 400, "Nome muito curto deveria retornar erro 400"
    assert exc_info.value.detail == "O nome deve ter entre 3 e 50 caracteres."


def test_name_too_long():
    with pytest.raises(HTTPException) as exc_info:
        validate_name("A" * 51)
    assert exc_info.value.status_code == 400, "Nome muito longo deveria retornar erro 400"
    assert exc_info.value.detail == "O nome deve ter entre 3 e 50 caracteres."


def test_name_with_numbers():
    with pytest.raises(HTTPException) as exc_info:
        validate_name("John Doe 123")
    assert exc_info.value.status_code == 400, "Nome com números deveria retornar erro 400"
    assert exc_info.value.detail == "O nome deve conter apenas letras e espaços."


def test_name_with_special_characters():
    with pytest.raises(HTTPException) as exc_info:
        validate_name("John@Doe!")
    assert exc_info.value.status_code == 400, "Nome com caracteres especiais deveria retornar erro 400"
    assert exc_info.value.detail == "O nome deve conter apenas letras e espaços."


def test_name_empty():
    with pytest.raises(HTTPException) as exc_info:
        validate_name("")
    assert exc_info.value.status_code == 400, "Nome vazio deveria retornar erro 400"
    assert exc_info.value.detail == "O nome não pode estar vazio."


# Valid email
def test_valid_email(repository_user):
    assert validate_email("newuser@example.com", repository_user) is True, "E-mail válido não foi aceito"


def test_invalid_email_format(repository_user):
    with pytest.raises(HTTPException) as exc_info:
        validate_email("invalid-email", repository_user)
    assert exc_info.value.status_code == 400, "Formato de e-mail inválido deveria retornar erro 400"
    assert exc_info.value.detail == "Formato de e-mail inválido."


def test_existing_email(client, repository_user):
    payload = {"name": "John Doe", "password": "#1234Abcd", "email": "johndoe@example.com"}
    create_user(client, **payload)

    with pytest.raises(HTTPException) as exc_info:
        validate_email(payload["email"], repository_user)
    assert exc_info.value.status_code == 400, "E-mail já existente deveria retornar erro 400"
    assert exc_info.value.detail == "Já existe um usuário registrado com este e-mail."


# Valid Password
def test_valid_password():
    assert validate_password("Str0ng!Password", "testuser") == True

def test_short_password():
    with pytest.raises(HTTPException):
        validate_password("short", "testuser")

def test_no_uppercase_password():
    with pytest.raises(HTTPException):
        validate_password("lowercase123!", "testuser")

def test_no_special_character_password():
    with pytest.raises(HTTPException):
        validate_password("NoSpecialChar123", "testuser")

def test_weak_password():
    with pytest.raises(HTTPException):
        validate_password("password", "testuser")

def test_password_contains_username():
    with pytest.raises(HTTPException):
        validate_password("Testuser123!", "testuser")






















