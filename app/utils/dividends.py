import pandas as pd
from datetime import datetime
from datetime import datetime, timedelta

from concurrent.futures import ThreadPoolExecutor
from functools import partial

def get_info_dividends_paid(asset_id, asset_history):
    """
    Retorna informações sobre o pagamento de dividendos de um ativo.

    is_recurring_dividends: Dividendos são pagos recorrentemente? 
    
    recurring_dividends_%: Porcentagem de recorrencia de pagamento

    """
    # TODO: O que acontece se um ativo não tem 12 meses de historico?
    current_date = datetime.now()
    date_one_year_ago = current_date - timedelta(days=365)
    date_one_year_ago = date_one_year_ago.strftime('%Y-%m-%d')

    
    df_asset_history = pd.DataFrame(asset_history)
    df_asset_history = df_asset_history[df_asset_history['date']>=date_one_year_ago]

    df_asset_history['date'] = pd.to_datetime(df_asset_history['date'])
    df_asset_history['month_year'] = df_asset_history['date'].dt.to_period('M')

    just_dividends = df_asset_history[df_asset_history['dividends']!=0]
    months_paid = len(just_dividends['month_year'])
    all_months = len(df_asset_history['month_year'].unique())
    percentage_months_paid = round((months_paid / (all_months-1)) * 100, 2)
    percentage_months_paid

    return {'asset_id': asset_id, 
        'is_recurring_dividends': months_paid==12,
        'recurring_dividends_%': round(percentage_months_paid, 2),
        'months_paid_freq': f'{months_paid}/{all_months-1}',
        'last_payment_quota': round(just_dividends['dividends'].iloc[-1], 2),
        'updated_unit_value': round(df_asset_history['close'].iloc[-1], 2),
        }

def get_calculate_monthly_percentage_variation(asset_id, asset_history, current_date=datetime.now(), previous_months=5):
    """
        Return
            	datas	variation_%	asset_id
            1	2020-03-01	3.29	99
            2	2020-04-01	-9.27	99
    """
    six_months_ago = current_date - timedelta(days=current_date.day - 1, weeks=4*previous_months)
    six_months_ago = datetime(six_months_ago.year, six_months_ago.month, 1).strftime('%Y-%m-%d')
    df_asset_history = pd.DataFrame(asset_history)
    df_asset_history = df_asset_history[df_asset_history['date']>=six_months_ago]
    
    # Supondo que 'Date' seja uma coluna do tipo datetime
    df_asset_history['date'] = pd.to_datetime(df_asset_history['date'])
    df_asset_history.set_index('date', inplace=True)

    # Calcular a valorização mensal desde o início do mês
    df_monthly_start = df_asset_history['close'].resample('MS').first()
    df_monthly_return = round(df_monthly_start.pct_change() * 100, 2)

    # Exibir o DataFrame resultante
    # return df_monthly_return
    df = pd.DataFrame({'data': pd.to_datetime(df_monthly_start.index), 'variation_%': df_monthly_return.tolist(), 'asset_id': asset_id})
    
    df['accumulated_variation_%'] = df['variation_%'].cumsum()
    # df.drop(index=0) pois o primeiro registro da variação é NaN
    df.drop(index=0, inplace=True)
    return df.to_dict("records")

def get_analyze_dividend_yield(asset_id:int, asset_history):
    """
    Cria um DataFrame contendo informações simuladas sobre a compra de cotas desses ativos ao longo de um ano. 
    Em seguida, realiza cálculos relacionados aos dividendos anuais, yield on cost anual e recebidos por cota anual para cada FII no portfólio simulado.

    list_ativos: Uma lista de códigos de ativos de fundos imobiliários (FIIs) para os quais a simulação será realizada.

    codigo_ativo: O código do ativo do FII.
    DY_anual: Dividend Yield anual, representando a porcentagem do dividendo em relação ao preço atual do ativo.
    yield_on_cost_anual: Yield on Cost anual, indicando o rendimento anual em relação ao custo original de aquisição das cotas.
    recebidos_por_cota_anual: Valor total de dividendos recebidos por cota ao longo do ano.
    """

    current_date = datetime.now()
    date_one_year_ago = current_date - timedelta(days=365)
    date_one_year_ago = date_one_year_ago.strftime('%Y-%m-%d')

    
    df_asset_history = pd.DataFrame(asset_history)
    df_asset_history = df_asset_history[df_asset_history['date']>=date_one_year_ago]

    average_value = df_asset_history['close'].mean()
    asset_dividends = df_asset_history[df_asset_history['dividends'] != 0]
    current_quota_value = df_asset_history['close'].iloc[-1]

    def calculate_analysis(df_iter_dividends):
        quantity=1
        received = round(df_iter_dividends['dividends'] * quantity, 2)
        total_cost = quantity * average_value

        serie = pd.Series({
            "asset_id": asset_id,
            "average_value": average_value,
            "current_quota_value": current_quota_value,
            "total_cost": total_cost,
            "yield_on_cost": (received / total_cost) * 100,
            "received_per_quota": received / quantity,
            "DY": (received / current_quota_value) * 100
        })

        return serie
    
    if len(asset_dividends['dividends']) == 0:
        return pd.DataFrame([{
            "asset_id": asset_id,
            "DY_annual_%":0.0,
            "yield_on_cost_anual_%":0.0,
            "received_by_annual_quota":0.0,
        }])

    list_analysis_annual = asset_dividends.apply(calculate_analysis, axis=1)

    list_analysis_annual['DY_annual_%'] = list_analysis_annual['DY']  # Renomeando a coluna DY
    list_analysis_annual['yield_on_cost_anual_%'] = round(list_analysis_annual['yield_on_cost'], 2) # Renomeando a coluna yield_on_cost
    list_analysis_annual['received_by_annual_quota'] = list_analysis_annual['received_per_quota']  # Renomeando a coluna recebidos_por_cota

    aggregate_result = list_analysis_annual.groupby('asset_id')[['DY_annual_%', 'yield_on_cost_anual_%', 'received_by_annual_quota']].sum().reset_index()

    return aggregate_result.to_dict("records")


import pandas as pd
from datetime import datetime
from datetime import datetime, timedelta

from concurrent.futures import ThreadPoolExecutor
from functools import partial

def get_info_dividends_paid(asset_id, asset_history):
    """
    Retorna informações sobre o pagamento de dividendos de um ativo.

    is_recurring_dividends: Dividendos são pagos recorrentemente? 
    
    recurring_dividends_%: Porcentagem de recorrencia de pagamento

    """
    # TODO: O que acontece se um ativo não tem 12 meses de historico?
    current_date = datetime.now()
    date_one_year_ago = current_date - timedelta(days=365)
    date_one_year_ago = date_one_year_ago.strftime('%Y-%m-%d')

    
    df_asset_history = pd.DataFrame(asset_history)
    df_asset_history = df_asset_history[df_asset_history['date']>=date_one_year_ago]

    df_asset_history['date'] = pd.to_datetime(df_asset_history['date'])
    df_asset_history['month_year'] = df_asset_history['date'].dt.to_period('M')

    just_dividends = df_asset_history[df_asset_history['dividends']!=0]
    months_paid = len(just_dividends['month_year'])
    all_months = len(df_asset_history['month_year'].unique())
    percentage_months_paid = round((months_paid / (all_months-1)) * 100, 2)
    percentage_months_paid

    return {'asset_id': asset_id, 
        'is_recurring_dividends': months_paid==12,
        'recurring_dividends_%': round(percentage_months_paid, 2),
        'months_paid_freq': f'{months_paid}/{all_months-1}',
        'last_payment_quota': round(just_dividends['dividends'].iloc[-1], 2),
        'updated_unit_value': round(df_asset_history['close'].iloc[-1], 2),
        }

def get_calculate_monthly_percentage_variation(asset_id, asset_history, current_date=datetime.now(), previous_months=5):
    """
        Return
            	datas	variation_%	asset_id
            1	2020-03-01	3.29	99
            2	2020-04-01	-9.27	99
    """
    six_months_ago = current_date - timedelta(days=current_date.day - 1, weeks=4*previous_months)
    six_months_ago = datetime(six_months_ago.year, six_months_ago.month, 1).strftime('%Y-%m-%d')
    df_asset_history = pd.DataFrame(asset_history)
    df_asset_history = df_asset_history[df_asset_history['date']>=six_months_ago]
    
    # Supondo que 'Date' seja uma coluna do tipo datetime
    df_asset_history['date'] = pd.to_datetime(df_asset_history['date'])
    df_asset_history.set_index('date', inplace=True)

    # Calcular a valorização mensal desde o início do mês
    df_monthly_start = df_asset_history['close'].resample('MS').first()
    df_monthly_return = round(df_monthly_start.pct_change() * 100, 2)

    # Exibir o DataFrame resultante
    # return df_monthly_return
    df = pd.DataFrame({'data': pd.to_datetime(df_monthly_start.index), 'variation_%': df_monthly_return.tolist(), 'asset_id': asset_id})
    
    df['accumulated_variation_%'] = df['variation_%'].cumsum()
    # df.drop(index=0) pois o primeiro registro da variação é NaN
    df.drop(index=0, inplace=True)
    return df.to_dict("records")

def get_analyze_dividend_yield(asset_id:int, asset_history):
    """
    Cria um DataFrame contendo informações simuladas sobre a compra de cotas desses ativos ao longo de um ano. 
    Em seguida, realiza cálculos relacionados aos dividendos anuais, yield on cost anual e recebidos por cota anual para cada FII no portfólio simulado.

    list_ativos: Uma lista de códigos de ativos de fundos imobiliários (FIIs) para os quais a simulação será realizada.

    codigo_ativo: O código do ativo do FII.
    DY_anual: Dividend Yield anual, representando a porcentagem do dividendo em relação ao preço atual do ativo.
    yield_on_cost_anual: Yield on Cost anual, indicando o rendimento anual em relação ao custo original de aquisição das cotas.
    recebidos_por_cota_anual: Valor total de dividendos recebidos por cota ao longo do ano.
    """

    current_date = datetime.now()
    date_one_year_ago = current_date - timedelta(days=365)
    date_one_year_ago = date_one_year_ago.strftime('%Y-%m-%d')

    
    df_asset_history = pd.DataFrame(asset_history)
    df_asset_history = df_asset_history[df_asset_history['date']>=date_one_year_ago]

    average_value = df_asset_history['close'].mean()
    asset_dividends = df_asset_history[df_asset_history['dividends'] != 0]
    current_quota_value = df_asset_history['close'].iloc[-1]

    def calculate_analysis(df_iter_dividends):
        quantity=1
        received = round(df_iter_dividends['dividends'] * quantity, 2)
        total_cost = quantity * average_value

        serie = pd.Series({
            "asset_id": asset_id,
            "average_value": average_value,
            "current_quota_value": current_quota_value,
            "total_cost": total_cost,
            "yield_on_cost": (received / total_cost) * 100,
            "received_per_quota": received / quantity,
            "DY": (received / current_quota_value) * 100
        })

        return serie
    
    if len(asset_dividends['dividends']) == 0:
        return pd.DataFrame([{
            "asset_id": asset_id,
            "DY_annual_%":0.0,
            "yield_on_cost_anual_%":0.0,
            "received_by_annual_quota":0.0,
        }])

    list_analysis_annual = asset_dividends.apply(calculate_analysis, axis=1)

    list_analysis_annual['DY_annual_%'] = list_analysis_annual['DY']  # Renomeando a coluna DY
    list_analysis_annual['yield_on_cost_anual_%'] = round(list_analysis_annual['yield_on_cost'], 2) # Renomeando a coluna yield_on_cost
    list_analysis_annual['received_by_annual_quota'] = list_analysis_annual['received_per_quota']  # Renomeando a coluna recebidos_por_cota

    aggregate_result = list_analysis_annual.groupby('asset_id')[['DY_annual_%', 'yield_on_cost_anual_%', 'received_by_annual_quota']].sum().reset_index()

    return aggregate_result.to_dict("records")


def calcular_patrimonio_e_rendimento(asset_id: int, df_wallet_history: pd.DataFrame) -> dict:
    """
    Calcula o patrimônio e rendimento de um ativo específico, com base no histórico da carteira.

    Args:
        asset_id (int): ID do ativo.
        df_wallet_history (pd.DataFrame): DataFrame contendo o histórico da carteira.

    Returns:
        dict: Dicionário contendo o valor atual, patrimônio, rendimento em reais e em porcentagem.
    """

    # Filtrar histórico válido
    df_valid_transactions = df_wallet_history.query("transaction_type_id != '-'").sort_values(by="date")

    # Filtrar histórico específico para o ativo
    df_asset_transactions = df_valid_transactions.query("asset_id == @asset_id")
    df_asset_history = df_wallet_history.query("asset_id == @asset_id")

    # Verificar se o histórico do ativo está vazio
    if df_asset_history.empty or df_asset_transactions.empty:
        return {
            'asset_id': asset_id,
            'valor_atual': 0.0,
            'patrimonio': 0.0,
            'rendimento_R$': 0.0,
            'rendimento_%': 0.0
        }

    # Obter o valor atual do ativo
    valor_atual_ativo = df_asset_history['close'].iloc[-1]

    # Calcular a quantidade total de ativos
    quantidade_total = df_asset_transactions['quantity'].sum()

    # Se não houver quantidade ou o valor atual for zero, o patrimônio é 0
    if quantidade_total == 0 or valor_atual_ativo == 0:
        return {
            'asset_id': asset_id,
            'valor_atual': round(valor_atual_ativo, 2),
            'patrimonio': 0.0,
            'rendimento_R$': 0.0,
            'rendimento_%': 0.0
        }

    # Calcular patrimônio
    patrimonio = valor_atual_ativo * quantidade_total

    # Calcular rendimento
    valor_total_compra = df_asset_transactions['purchase_value'].sum()
    rendimento_reais = patrimonio - valor_total_compra

    # Evitar divisão por zero ao calcular rendimento percentual
    rendimento_percentual = (
        (rendimento_reais / valor_total_compra) * 100
        if valor_total_compra > 0 else 0.0
    )

    # Retornar resultados arredondados
    return {
        'asset_id': asset_id,
        'valor_atual': round(valor_atual_ativo, 2),
        'patrimonio': round(float(patrimonio), 2),
        'rendimento_R$': round(float(rendimento_reais), 2),
        'rendimento_%': round(float(rendimento_percentual), 2)
    }


def get_process_asset(wallet_history):
    """
    Processa o cálculo de patrimônio e rendimento para todos os ativos de uma carteira.

    Args:
        df_wallet_history (pd.DataFrame): DataFrame contendo o histórico da carteira.

    Returns:
        pd.DataFrame: DataFrame com os resultados de patrimônio e rendimento de cada ativo.
    """
    df_wallet_history = pd.DataFrame(wallet_history)
    
    # Usar ThreadPoolExecutor para paralelismo
    with ThreadPoolExecutor() as executor:
        # Usar partial para passar argumentos fixos à função
        func = partial(calcular_patrimonio_e_rendimento, df_wallet_history=df_wallet_history)
        asset_ids = df_wallet_history['asset_id'].unique()
        asset_reports = list(executor.map(func, asset_ids))

    # Converter resultados em DataFrame
    return asset_reports


