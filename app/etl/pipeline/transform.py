from typing import Dict, List
import pandas as pd
from collections import defaultdict

def transform_stock_data(df_extract_data: pd.DataFrame, dict_asset_process:Dict) -> Dict[str, Dict[str, List]]:
    """
    Transforma um DataFrame com dados de múltiplos FIIs em um dicionário organizado.

    Args:
        df_extract_data (pd.DataFrame): DataFrame de entrada com colunas multi-nível.

    Returns:
        dict: Dicionário organizado com dados por FII.
    """
    # Extrai os FIIs selecionados a partir do nível de colunas
    asset_selected = dict_asset_process.keys()

    # Inicializa o dicionário de resultados
    dict_transform_stock_data = {fii: defaultdict(list) for fii in asset_selected}
    dict_transform_stock_data.update(dict_asset_process)

    for price_column, ticker_column in df_extract_data:
        
        df_without_nan =  df_extract_data[price_column][ticker_column].dropna()

        price_column_sep = "_".join(price_column.split())
        price_column_lower = price_column_sep.lower()
        dict_transform_stock_data[ticker_column][price_column_lower] = df_without_nan.tolist()

        dict_transform_stock_data[ticker_column]['date'] = df_without_nan.reset_index()['Date'].tolist()

    return dict_transform_stock_data