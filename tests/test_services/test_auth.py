import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.infra.config.database import Base, get_db
from app.main import app
from app.settings.config import Settings

settings = Settings()

# Configuração do banco de dados para testes
engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Criando o banco de dados
Base.metadata.create_all(bind=engine)

# Fixture para sessão de banco de dados de teste
@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session  # Disponibiliza a sessão para os testes

    session.close()
    transaction.rollback()
    connection.close()


# Fixture para cliente de teste
@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

# Teste para criar um usuário
def test_create_user(client):
    payload = {"name": "John Doe", 
               "password": "123456789",
                "email": "johndoe@example.com"}
    
    response = client.post("/signup", json=payload)
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "John Doe"
    assert data["email"] == "johndoe@example.com"
    assert "id" in data

























