from app.PortfolioManager.utils.auxiliary_functions import repository_portfolio_manage
from datetime import datetime
import pandas as pd
from app.schemas.constants.enums import TransactionTypeEnum
from app.repository.portfolio import RepositoryPortfolio
from typing import Optional
from app.infra.config.database import get_db_session
# TODO: Ativos vendidos são considerados no calculo ex: ativo ABCS11 teve 10, 10, e 10 de compra e 10 de venda, no final ele tem 30 e não 20
from concurrent.futures import ThreadPoolExecutor

def gera_relatorio_valorizacao_anual(asset_id, start='2023-12-31'):
    """
    Gera porcentagem de retornos ao longo do tempo.
    """
    with get_db_session() as session:
        repository_portfolio = RepositoryPortfolio(session=session)
        historico_precos = repository_portfolio.history(asset_id, start=start)

        df_historico_precos = pd.DataFrame(historico_precos)
        if df_historico_precos.empty:
            return {}

        preco_inicial = df_historico_precos['close'].iloc[0]
        preco_final = df_historico_precos['close'].iloc[-1]
        rendimento_anual = ((preco_final / preco_inicial) - 1) * 100

        return {
            'asset_id': asset_id,
            'valor_atual': round(preco_final, 2),
            'valorizacao_12M_%': round(rendimento_anual, 2),
            'min_52_semanas': round(df_historico_precos['close'].min(), 2),
            'max_52_semanas': round(df_historico_precos['close'].max(), 2),
            'dividendos_pagos_ano': round(df_historico_precos['dividends'].sum(), 2)
        }

def dividends_received_history(df_transaction_history, end: Optional[datetime] = None):
    """
    Gera o histórico de dividendos recebidos por ativo.

    :param df_transaction_history: DataFrame com histórico de transações.
    :param end: Data final opcional para análise.
    :return: DataFrame contendo o histórico de dividendos recebidos.
    """
    list_historico_dividendos_recebidos = []
    df_transaction_history_copy = df_transaction_history.copy()

    for asset_id in set(df_transaction_history_copy['asset_id'].tolist()):
        df_dados_ativo = df_transaction_history_copy[df_transaction_history_copy['asset_id'] == asset_id]
        start = df_dados_ativo['date'].min()

        with get_db_session() as session:
            repository_portfolio = RepositoryPortfolio(session=session)
    
            historico_precos = repository_portfolio.history(asset_id, start=start, end=end)
            df_historico_precos = pd.DataFrame(historico_precos)

        if df_historico_precos.empty:
            continue

        relatorio_anual = gera_relatorio_valorizacao_anual(asset_id, start=start)
        valor_medio = df_historico_precos['close'].mean()
        valor_atual_cota = df_historico_precos['close'].iloc[-1]
        ativo_dividends = df_historico_precos[df_historico_precos['dividends'] != 0]

        for _, df_iter_dividends in ativo_dividends.iterrows():
            quantity = (
                df_dados_ativo[
                    (df_dados_ativo['date'] <= df_iter_dividends['date']) &
                    (df_dados_ativo['transaction_type_id'] == TransactionTypeEnum.COMPRA_ID.value)
                ]['quantity'].sum()
                - df_dados_ativo[
                    (df_dados_ativo['date'] <= df_iter_dividends['date']) &
                    (df_dados_ativo['transaction_type_id'] == TransactionTypeEnum.VENDA_ID.value)
                ]['quantity'].sum()
            )

            recebidos = round(df_iter_dividends['dividends'] * quantity, 2)
            custo_total = quantity * valor_medio
            yield_on_cost = 0 if custo_total == 0 else (recebidos / custo_total) * 100
            recebidos_por_cota = 0 if quantity == 0 else recebidos / quantity
            DY = (recebidos_por_cota / valor_atual_cota) * 100
            date_pagamento = df_iter_dividends['date'].strftime('%Y-%m-%d')

            list_historico_dividendos_recebidos.append({
                'asset_id': asset_id,
                'recebidos': recebidos,
                'transaction_type_id': df_dados_ativo['transaction_type_id'].iloc[0],
                'date_pagamento': date_pagamento,
                'yield_on_cost_mes_%': round(yield_on_cost, 2),
                'DY_mes_%': round(DY, 2),
                'quantity': quantity,
                'valor_medio': round(valor_medio, 2),
                'recebidos_por_cota': round(recebidos_por_cota, 2),
                **relatorio_anual
            })

    return pd.DataFrame(list_historico_dividendos_recebidos)



# DY_mes_%, yield_on_cost_mes_%, min_52_semanas,	max_52_semanas,	valorização(12M)




############################################################

