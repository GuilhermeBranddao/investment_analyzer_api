import os
from urllib.parse import urlparse
import logging
from sqlalchemy import create_engine, MetaData, Table, Column, Date, Float, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
# from sqlalchemy.rom.declarative import declarative_base

Base = declarative_base()

class Database_Deprecado:
    """
    Classe para gerenciar a configuração e operações do banco de dados.
    """
    def __init__(self, database_url=None):
        """
        Inicializa o banco de dados.
        
        Args:
            database_url (str): URL do banco de dados (opcional). Usa o padrão se não fornecido.
        """
        self.database_url = (
            database_url
            if database_url and urlparse(database_url).scheme
            else os.getenv("DATABASE_URL", "sqlite:///app/data/database/stocks_data.db")
        )
        self.engine = create_engine(self.database_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)
        
    
    def get_session(self):
        """
        Retorna uma nova sessão do banco de dados.
        """
        return self.Session()

    def get_engine(self):
        return self.engine

    def close_session(self, session):
        """
        Fecha uma sessão do banco de dados.
        
        Args:
            session (Session): Sessão do banco a ser fechada.
        """
        try:
            session.close()
            self.engine = None
        except Exception as e:
            logging.warning(f"Erro ao fechar sessão: {e}")


