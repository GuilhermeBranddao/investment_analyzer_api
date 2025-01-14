from app.etl.pipeline.extract import extract_stock_data
from app.etl.pipeline.transform import transform_stock_data
from app.etl.pipeline.load import load_data_to_db
from datetime import datetime
import logging
from app.settings.config import Settings
from app.infra.config.database import get_session_local, create_all_tables, create_engine_db
from app.infra.database.database import Base

settings = Settings()

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)

def main():
    # Configurações


    create_all_tables(engine=create_engine_db(DATABASE_URL=settings.DATABASE_URL), 
                    Base=Base)
    set_ticker = {
        'HABT11.SA', 'OUJP11.SA', 'PLCR11.SA', 'MXRF11.SA', 
        'DVFF11.SA', 'BMLC11.SA', 'BIME11.SA',
        'JPPA11.SA', 'RBRY11.SA', 'VGIR11.SA', 'GALG11.SA', 'AAZQ11.SA', 'BRCR11.SA', 'CPTR11.SA',
        'CRFF11.SA', 'CVBI11.SA', 'CXCI11.SA', 'CXRI11.SA', 'DCRA11.SA', 'FAED11.SA', 'FLCR11.SA',
        'HGCR11.SA', 'HSAF11.SA', 'KNCA11.SA', 'MGFF11.SA', 'QAGR11.SA', 'RBRL11.SA', 'RECR11.SA',
        'RECT11.SA', 'RURA11.SA', 'RZAG11.SA', 'SEQR11.SA', 'URPR11.SA', 'VCRA11.SA', 'VGIA11.SA',
        'VGHF11.SA', 'RBRF11.SA', 'KNCR11.SA',

        'ITSA4.SA', 'SAPR4.SA', 'CPLE6.SA', 'BBAS3.SA', 'BBDC3.SA', 'BBSE3.SA', 'BRCO11.SA',
        'HGCR11.SA', 'IRDM11.SA', 'ITUB3.SA', 'VALE3.SA', 'WEGE3.SA', 'BCRI11.SA', 'PORD11.SA',
        'MXRF11.SA', 'HABT11.SA', 'JPPA11.SA', 'VGIR11.SA', 'OUJP11.SA', 'GALG11.SA',
        'KNCR11.SA'
    }
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
