from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.settings.config import Settings
from contextlib import contextmanager

settings = Settings()

engine = create_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def criar_bd():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    
@contextmanager
def get_db_session():
    """Gerencia a sessão do banco de dados."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()