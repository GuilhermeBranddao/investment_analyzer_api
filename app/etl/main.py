from app.etl.pipeline.extract import extract_stock_data
from app.etl.pipeline.transform import transform_stock_data
from app.etl.pipeline.load import load_data_to_db
from datetime import datetime
import logging
from app.settings.config import Settings
from app.infra.config.database import get_session_local, create_all_tables, create_engine_db
from app.infra.database.database import Base
import pandas as pd

settings = Settings()

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)

def main():
    # Configurações
    print(f">>>>>>: {settings.DATABASE_URL}")
    engine = create_engine_db(settings.DATABASE_URL)
    create_all_tables(engine, Base)
    
    # FIXME: Criar uma variavel de ambiente pra esses dados
    df = pd.read_csv("app/data/file_fii_csv/list_assets.csv")
    
    set_ticker = set(df["list_assets"].tolist())
    
    start_date = None
    today = datetime.now()
    end_date = today.strftime('%Y-%m-%d')

    # Extração
    df_extract_data, dict_asset_process = extract_stock_data(set_ticker, start_date, end_date)
    logging.info("Extração concluída.")

    # Transformação
    dict_transformed_data = transform_stock_data(df_extract_data, dict_asset_process)
    logging.info("Transformação concluída.")

    # Exemplo de operações no banco
    logging.info("Banco de dados configurado e pronto para uso.")

    # Carregamento
    load_data_to_db(dict_transformed_data)
    logging.info("Dados carregados no banco de dados com sucesso.")
    
    

if __name__ == "__main__":
    main()
