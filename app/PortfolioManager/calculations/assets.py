import numpy as np
import datetime as dt
import pandas as pd
from app.PortfolioManager.utils.auxiliary_functions import repository_portfolio_manage

def validate_purchase_date_vectorized(dates):
    """
    Valida uma série de datas de compra.
    """
    today = dt.date.today()
    dates_parsed = pd.to_datetime(dates, errors='coerce')
    return dates_parsed.dt.date <= today

def calculate_portfolio_metrics_vectorized(df_prices, df_transactions):
    """
    Calcula métricas do portfólio de forma vetorizada.
    """
    
    latest_prices = df_prices.groupby('asset_id')[['close']].last()
    latest_prices.reset_index(inplace=True)
    latest_prices.rename(columns={"close":"close_atual"}, inplace=True)

    df_transactions = pd.merge(
        df_transactions, 
        latest_prices, 
        on='asset_id',
        how='left'
    )


   
    df_transactions['patrimonio'] = df_transactions['close_atual'] * df_transactions['quantity']
    df_transactions['rendimento_R$'] = df_transactions['patrimonio'] - df_transactions['purchase_value']
    df_transactions['rendimento_%'] = (df_transactions['rendimento_R$'] / df_transactions['purchase_value']) * 100

    df_transactions = df_transactions.fillna(0)
    
    df_transactions['valor_atual'] = df_transactions["quantity"] * df_transactions["close_atual"]

    return df_transactions[['valor_atual', 'patrimonio', 'rendimento_R$', 'rendimento_%']]

def calculate_portfolio_value_optimized(df_transaction_history):
    """
    Calcula o patrimônio e os rendimentos do portfólio de forma otimizada.
    """
    df_transacoes = df_transaction_history.copy()
    df_transacoes.sort_values(by='date', inplace=True)

    # Validação de datas de forma vetorizada
    valid_dates = validate_purchase_date_vectorized(df_transacoes['date'])
    df_transacoes = df_transacoes[valid_dates]

    # Buscar histórico de preços em uma única consulta
    repository_portfolio = repository_portfolio_manage()
    
    df_transaction_history['asset_name'] = df_transaction_history['asset_id'].apply(lambda x: repository_portfolio.get_asset_name_per_id(x).replace('.SA', ''))
    df_transaction_history['transaction_type__name'] = df_transaction_history['transaction_type_id'].apply(lambda x: repository_portfolio.get_transaction_type_name_per_id(x))
    
    asset_ids = df_transacoes['asset_id'].unique()
    all_price_histories = [
        pd.DataFrame(repository_portfolio.history(asset_id=asset_id)).assign(asset_id=asset_id)
        for asset_id in asset_ids
    ]
    df_prices = pd.concat(all_price_histories, ignore_index=True)

    # Calcular métricas de forma vetorizada
    metrics = calculate_portfolio_metrics_vectorized(df_prices, df_transacoes)
    df_transacoes.update(metrics)

    return df_transacoes
