import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from urllib.parse import urlparse
from app.settings.config import Settings
from app.models.models import *

settings = Settings()

def create_engine_db(DATABASE_URL: str) -> create_engine:
    """Função para criar o engine e garantir que o diretório do banco de dados existe"""
    parsed_url = urlparse(DATABASE_URL)
    db_path = parsed_url.path[1:]  # Remover a barra inicial do caminho
    db_dir = os.path.dirname(db_path)

    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}
    )
    return engine

# Função para obter a base declarativa (deve ser criada uma vez)
Base = declarative_base()

def create_all_tables(engine, Base):
    """Função para criar as tabelas no banco de dados"""
    Base.metadata.create_all(bind=engine)

def get_session_local(DATABASE_URL: str = settings.DATABASE_URL):
    engine = create_engine_db(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def get_db():
    """
    Função para obter a sessão de banco de dados
    """
    DATABASE_URL: str = settings.DATABASE_URL
    engine = create_engine_db(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_session(DATABASE_URL: str = settings.DATABASE_URL):
    """
    Context manager para obter a sessão de banco de dados com gerenciamento automático
    """
    engine = create_engine_db(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
