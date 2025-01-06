import pandas as pd
import logging
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine
from contextlib import contextmanager
from app.infra.config.database import get_db
from sqlalchemy import text

from app.models.models import Asset
from sqlalchemy.exc import NoResultFound
# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Context Manager para gerenciar sessão do banco
@contextmanager
def db_session():
    """
    Gerenciador de contexto para obter uma sessão do banco de dados.
    """
    db = get_db()
    session = next(db)  # Consumir o gerador para obter a sessão
    try:
        yield session
    finally:
        session.close()

# Função para verificar dados existentes
def get_existing_dates(asset_id, session, table="asset_price_history"):
    """
    Retorna as datas já existentes no banco para um asset_id específico.

    Args:
        asset_id (str): asset_id da ação.
        session: Sessão do banco de dados.
        table (str): Nome da tabela no banco de dados.

    Returns:
        set: Conjunto de datas existentes.
    """
    query = text(f"SELECT date FROM {table} WHERE asset_id = :asset_id")
    try:
        result = session.execute(query, {"asset_id": asset_id}).fetchall()
        # FIXME: Quero tirar o pd.to_datetime dessa iteração
        return set(pd.to_datetime(row[0]) for row in result)
    except SQLAlchemyError as e:
        logging.error(f"Erro ao buscar datas existentes para o asset_id {asset_id}: {e}")
        return set()


# Função principal para carregar dados
def load_data_to_db(dict_transformed_stock_data):
    """
    Carrega os dados transformados para o banco de dados.

    Args:
        dict_transformed_stock_data (dict): Dicionário contendo dados transformados.
    """
    with db_session() as session:
        for ticker, data in dict_transformed_stock_data.items():
            try:
                # Converter dados para DataFrame
                df = pd.DataFrame(data)
                df = df[["date", "open", "high", "low", "close", "dividends", "stock_splits", "volume"]]
                asset_id = get_or_create_asset(ticker)
                df["asset_id"] = asset_id

                # Obter datas existentes no banco
                existing_dates = get_existing_dates(asset_id, session)

                # Filtrar novos dados
                df["date"] = pd.to_datetime(df["date"])  # Garantir formato de data
                df = df[~df["date"].isin(existing_dates)]

                if not df.empty:
                    # Inserir novos dados no banco
                    df.to_sql("asset_price_history", con=session.bind, if_exists="append", index=False)
                    logging.info(f"Dados do ticker {ticker} inseridos com sucesso!")
                else:
                    logging.info(f"Sem novos dados para o ticker {ticker}.")
            except Exception as e:
                logging.error(f"LOAD: Erro ao processar dados do ticker {ticker}: {e}")



def get_or_create_asset(ticker: str, name: str = None, category: str = None):
    """
    Verifica se o ativo já existe no banco e o cria se necessário.
    Retorna o asset_id.
    """
    with db_session() as session:
        try:
            asset = session.query(Asset).filter_by(symbol=ticker).one()
            return asset.id
        except NoResultFound:
            new_asset = Asset(
                symbol=ticker,
                name=name if name else f"Unknown Name for {ticker}",
                category=category if category else "Unknown"
            )
            session.add(new_asset)
            session.commit()
            return new_asset.id