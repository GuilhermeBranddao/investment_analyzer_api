import yfinance as yf
import pandas as pd
from datetime import datetime
from datetime import datetime, timedelta
#from database.db_generic import history
#from utils import get_ativos_in_carteira

def gera_relatorio_valorizacao_anual(ativo):
    """
    Gera porcentagem de retornos ao longo do tempo
    """
    start = '2022-07-16' # TODO: add data de um ano atras
    list_retornos = []

    # ativo_download = yf.download(ativo+'.SA', start=start, actions=True, progress=False)
    historico_precos = history(ativo=ativo, 
                                 start=start)

    # Calcular o rendimento anual
    preco_inicial = historico_precos['Close'].iloc[0]
    preco_final = historico_precos['Close'].iloc[-1]
    rendimento_anual = ((preco_final / preco_inicial) - 1) * 100

    list_retornos = {
        'codigo_ativo':ativo, 
        'valor_atual':round(preco_final, 2),
        'min_52_semanas':round(historico_precos['Close'].min(), 2),
        'max_52_semanas':round(historico_precos['Close'].max(), 2),
        'valorização(12M)':round(rendimento_anual, 2),
        'dividendos_pagos_ano': round(historico_precos['Dividends'].sum(), 2)
        }
    return list_retornos

def historico_dividendos_recebidos(df_transaction_history, end=None):
    # TODO: Vi um possivel erro
        # A função calcula em um ranger de datas totais
        # Assim se tiver um ativo repetido no historico 
        # É calculado tambem (Verificar)
    
    # TODO: Ativos vendidos são considerados no calculo ex: ativo ABCS11 teve 10, 10, e 10 de compra e 10 de venda, no final ele tem 30 e não 20

        # Add investimento total
    list_historixo_dividendos_recebidos = []
    df_transaction_history_copy = df_transaction_history.copy()

    for ativo in df_transaction_history_copy['codigo_ativo'].unique():
        df_dados_ativo = df_transaction_history_copy[df_transaction_history_copy['codigo_ativo'] == ativo]
        start = df_dados_ativo['data'].min()#'2023-02-09' #df_iter['data']

        historico_precos = history(ativo=ativo, 
                                    start=start,
                                    end=end)
        # Calcular o rendimento anual
        list_retornos = gera_relatorio_valorizacao_anual(ativo)
        min_52_semanas = list_retornos['min_52_semanas']
        max_52_semanas = list_retornos['max_52_semanas']
        valorizacao_12M = list_retornos['valorização(12M)']
        dividendos_pagos_ano = list_retornos['dividendos_pagos_ano']

        valor_medio = historico_precos['Close'].mean()
        valor_atual_cota = historico_precos['Close'].iloc[-1]
        ativo_dividends = historico_precos[historico_precos['Dividends']!=0]

        for index_dividends, df_iter_dividends in ativo_dividends.iterrows():

            quantidade = df_dados_ativo[(df_dados_ativo['data']<=str(df_iter_dividends['Date'])) & (df_dados_ativo['evento']=='Compra')]['quantidade'].sum()
            quantidade -= df_dados_ativo[(df_dados_ativo['data']<=str(df_iter_dividends['Date'])) & (df_dados_ativo['evento']=='Venda')]['quantidade'].sum()

            valor_unitario = round(historico_precos[historico_precos['Date']==df_iter_dividends['Date']]['Close'].iloc[0], 2)

            recebidos = round(df_iter_dividends['Dividends'] * quantidade, 2)
            custo_total = quantidade * valor_medio

            # yield_on_cost = (recebidos / custo_total) * 100
            yield_on_cost = 0 if recebidos + custo_total == 0 else (recebidos / custo_total) * 100
            recebidos_por_cota = 0 if recebidos + quantidade == 0 else recebidos / quantidade

            DY = (recebidos_por_cota / valor_atual_cota) * 100
            data_pagamento = datetime.strftime(df_iter_dividends['Date'], '%Y-%m-%d')

            list_historixo_dividendos_recebidos.append({
                'codigo_ativo':ativo, 
                'recebidos':recebidos, 
                'categoria':df_dados_ativo['categoria'].iloc[0],
                'data_pagamento':data_pagamento,
                'yield_on_cost_mes_%': round(yield_on_cost, 2),
                'DY_mes_%':round(DY, 2),
                'quantidade':quantidade,
                'valor_medio': round(valor_medio, 2),
                # 'valor_unitario':valor_unitario,
                'recebidos_por_cota': round(recebidos_por_cota, 2),
                # 'valor_compra': df_dados_ativo['valor_compra'].item(),

                # Calcular o rendimento anual
                'min_52_semanas':min_52_semanas,
                'max_52_semanas':max_52_semanas,
                'valorizacao_12M':valorizacao_12M,
                'dividendos_pagos_ano': dividendos_pagos_ano
                }
            )
    
    return pd.DataFrame(list_historixo_dividendos_recebidos)


def calcular_estatisticas_dividendos(df_historico_dividendos):
    """
    Calcula estatísticas relevantes relacionadas a dividendos com base nos dados fornecidos.

    Parâmetros:
    - df_historico_dividendos (pandas.DataFrame): DataFrame contendo os dados históricos de dividendos recebidos por ativo.

    Retorno:
    - final_df (pandas.DataFrame): DataFrame final contendo as estatísticas calculadas.


    # Add total_investido
    # Quantidade de cotas
    """

    # Agrupar os dados pelo código do ativo e calcular estatísticas relevantes
    grouped = df_historico_dividendos.groupby('codigo_ativo').agg({
        'recebidos': ['sum', 'mean'],
        'valor_unitario': 'mean',
        'dividendos_pagos_ano': 'sum', #  # TODO: Não é por ano e sim pelo periudo presente no dataframe
        'min_52_semanas': 'min', # TODO: Não é por ano e sim pelo periudo presente no dataframe
        'max_52_semanas': 'max', # TODO: Não é por ano e sim pelo periudo presente no dataframe
        'valorizacao_12M': 'mean' # TODO: Não é por ano e sim pelo periudo presente no dataframe
    })

    # Calcular DY (Dividend Yield)
    grouped['DY'] = (grouped['recebidos']['sum'] / grouped['valor_unitario']['mean']) * 100

    # Criar o dataframe final com as colunas desejadas
    final_df = pd.DataFrame({
        'codigo_ativo': grouped.index,
        'recebidos_tot': grouped['recebidos']['sum'],
        'recebidos_mean': grouped['recebidos']['mean'].round(2),
        'DY': grouped['DY'].round(2),
        'min_52_semanas': grouped['min_52_semanas'].iloc[:, 0],  # Ajuste para obter o valor mínimo corretamente
        'max_52_semanas': grouped['max_52_semanas'].iloc[:, 0],
        'valorizacao_12M': grouped['valorizacao_12M'].iloc[:, 0],
        'dividendos_pagos_ano': grouped['dividendos_pagos_ano'].iloc[:, 0]
    })

    final_df.reset_index(drop=True, inplace=True)  # Redefinir o índice

    return final_df

def calcular_custo_medio(df_transaction_history:pd.DataFrame, ativo:str):
    """

    Calcula o custo médio de um ativo no portfólio.

    O que é custo médio?
        - É o custo de cada aquisição individual de uma ação somado e dividido pelo total de ações adiquiridas
        ex:
            list_compras = np.sum([1000, 3600, 2800])
            list_quantidade = np.sum([100, 300, 200])
            custo_medio = list_compras/list_quantidade

            Supomos que hoje a ação EASY1 está valendo R$15 e o custo medio da sua ação está 12.33  
            Considerando que no exemplo você tem o total de 600 Ações da EASY1 sua carteira valorizou R$1602 (600 * (15-12.33))
    """
    df = df_transaction_history[df_transaction_history['codigo_ativo'] == ativo]

    if df['quantidade'].sum() <= 0:
        return {'codigo_ativo': ativo, 
            'custo_medio': 0}

    return {'codigo_ativo': ativo, 
            'custo_medio': round(df['valor_compra'].sum()/df['quantidade'].sum(), 2)}

def info_dividendos_pagos(ativo):
    """
    Retorna informações sobre o pagamento de dividendos de um ativo.

    is_recurring_dividends: Dividendos são pagos recorrentemente? 
    
    recurring_dividends_%: Porcentagem de recorrencia de pagamento

    """
    # TODO: O que acontece se um ativo não tem 12 meses de historico?
    data_atual = datetime.now()
    data_um_ano_atras = data_atual - timedelta(days=365, weeks=0)
    data_um_ano_atras = data_um_ano_atras.strftime('%Y-%m-%d')

    df_history = history(ativo=ativo, 
                         start=data_um_ano_atras, 
                         end=None)

    df_history['Date'] = pd.to_datetime(df_history['Date'])
    df_history['mes_ano'] = df_history['Date'].dt.to_period('M')

    so_dividendos = df_history[df_history['Dividends']!=0]
    meses_pagos = len(so_dividendos['mes_ano'])
    todos_meses = len(df_history['mes_ano'].unique())
    porcentagem_meses_pagos = round((meses_pagos / (todos_meses-1)) * 100, 2)
    porcentagem_meses_pagos

    return {'codigo_ativo': ativo, 
        'is_recurring_dividends': meses_pagos==12,
        'recurring_dividends_%': round(porcentagem_meses_pagos, 2),
        'meses_pagos_freq': f'{meses_pagos}/{todos_meses-1}',
        'ultimo_pagamento_cota': round(so_dividendos['Dividends'].iloc[-1], 2),
        'valor_unitario_atualizado': round(df_history['Close'].iloc[-1], 2),
        }


# Relatorio de ativos

def analise_anual_dividendos_fii(ativo):
    """
    Cria um DataFrame contendo informações simuladas sobre a compra de cotas desses ativos ao longo de um ano. 
    Em seguida, realiza cálculos relacionados aos dividendos anuais, yield on cost anual e recebidos por cota anual para cada FII no portfólio simulado.

    list_ativos: Uma lista de códigos de ativos de fundos imobiliários (FIIs) para os quais a simulação será realizada.

    codigo_ativo: O código do ativo do FII.
    DY_anual: Dividend Yield anual, representando a porcentagem do dividendo em relação ao preço atual do ativo.
    yield_on_cost_anual: Yield on Cost anual, indicando o rendimento anual em relação ao custo original de aquisição das cotas.
    recebidos_por_cota_anual: Valor total de dividendos recebidos por cota ao longo do ano.
    """

    data_atual = datetime.now()
    data_um_ano_atras = data_atual - timedelta(days=365, weeks=4)
    data_um_ano_atras = data_um_ano_atras.strftime('%Y-%m-%d')

    historico_precos = history(ativo=ativo, start=data_um_ano_atras)

    valor_medio = historico_precos['Close'].mean()
    ativo_dividends = historico_precos[historico_precos['Dividends'] != 0]
    valor_atual_cota = historico_precos['Close'].iloc[-1]

    def calcular_analise(df_iter_dividends):
        quantidade=1
        recebidos = round(df_iter_dividends['Dividends'] * quantidade, 2)
        custo_total = quantidade * valor_medio

        serie = pd.Series({
            "codigo_ativo": ativo,
            "valor_medio": valor_medio,
            "valor_atual_cota": valor_atual_cota,
            "custo_total": custo_total,
            "yield_on_cost": (recebidos / custo_total) * 100,
            "recebidos_por_cota": recebidos / quantidade,
            "DY": (recebidos / valor_atual_cota) * 100
        })

        return serie
    
    if len(ativo_dividends['Dividends']) == 0:
        return pd.DataFrame([{
            "codigo_ativo": ativo,
            "DY_anual_%":0.0,
            "yield_on_cost_anual_%":0.0,
            "recebidos_por_cota_anual":0.0,
        }])

    list_analise_anual = ativo_dividends.apply(calcular_analise, axis=1)

    list_analise_anual['DY_anual_%'] = list_analise_anual['DY']  # Renomeando a coluna DY
    list_analise_anual['yield_on_cost_anual_%'] = round(list_analise_anual['yield_on_cost'], 2) # Renomeando a coluna yield_on_cost
    list_analise_anual['recebidos_por_cota_anual'] = list_analise_anual['recebidos_por_cota']  # Renomeando a coluna recebidos_por_cota

    resultado_agregado = list_analise_anual.groupby('codigo_ativo')[['DY_anual_%', 'yield_on_cost_anual_%', 'recebidos_por_cota_anual']].sum().reset_index()

    return resultado_agregado

def historic_DY_emojis(ativo):
    """
        Recebe o df_historico_dividendos e ativo e retorna "[💤, 🟢, 💣, 💣, 💣, ⏳]"
    """
    data_atual = datetime.now()
    seis_meses_atras = data_atual - timedelta(weeks=21)
    seis_meses_atras = seis_meses_atras.strftime('%Y-%m-%d')

    df_history = history(ativo=ativo, start=seis_meses_atras, end=None)

    df_history['Date'] = pd.to_datetime(df_history['Date'])
    df_history['mes_ano'] = df_history['Date'].dt.to_period('M')

    todos_meses = df_history['mes_ano'].unique().tolist()

    df_history = df_history[df_history['Dividends']!=0]

    list_check_DY = []

    emojis_DY = []

    if df_history.shape[0] == 0:
        list_check_DY.append({'codigo_ativo':ativo, 
                            'historic_DY_emojis_meses':['❓']})
        return pd.DataFrame(list_check_DY)


    for mes_ano in todos_meses:
        try:
            mes_ano >= df_history[df_history['Date'] == df_history['Date'].max()]['mes_ano'].item()
        except:
            breakpoint()

        if mes_ano in df_history['mes_ano'].tolist():
            # '🟢' para ativos que pagam acima de 1.0% de DY e '🔴' se pagar abaixo de 1.0% de DY
            df_filtered = df_history[df_history['mes_ano'] == mes_ano]
            dy = df_filtered['Dividends'].sum() / df_filtered['Close'].mean() * 100
            emojis_DY.append('🟢' if dy >= 1.0 else '🔴')
        elif mes_ano < df_history['mes_ano'].min():
            # Caso o ativo seja novo e ainda não há historico de dividendos
            # emojis_DY.append('💤')
            pass
        elif mes_ano >= df_history[df_history['Date'] == df_history['Date'].max()]['mes_ano'].item():
            # Caso o ativo ainda não pagou o dividendo estando no mês atual
            emojis_DY.append('⏳')
        elif mes_ano not in df_history['mes_ano'].tolist():
            # Caso o ativo não tenha pago dividendos
            emojis_DY.append('💣')
        else:
            # Caso alguma coisa estranha tenha ocorrido
            emojis_DY.append('❓')

    list_check_DY.append({'codigo_ativo':ativo, 
                        'historic_DY_emojis_meses':emojis_DY})

    return pd.DataFrame(list_check_DY)

def calcular_variacao_percentual_mensal(ativo, data_atual=None, meses_anteriores=5):
    """
        Return
            	datas	variacao_%	codigo_ativo
            1	2020-03-01	3.29	JPPA11
            2	2020-04-01	-9.27	JPPA11
    """
    if data_atual:
        data_atual = datetime.strptime(data_atual, '%Y-%m-%d')
    else:
        data_atual = datetime.now()
    
    seis_meses_atras = data_atual - timedelta(days=data_atual.day - 1, weeks=4*meses_anteriores)
    seis_meses_atras = datetime(seis_meses_atras.year, seis_meses_atras.month, 1).strftime('%Y-%m-%d')

    # print(seis_meses_atras)
    historico_ativo = history(ativo=ativo, start=seis_meses_atras).copy()
    # historico_ativo = historico_ativo[historico_ativo['Date'] >= seis_meses_atras].copy()
    
    # Supondo que 'Date' seja uma coluna do tipo datetime
    historico_ativo['Date'] = pd.to_datetime(historico_ativo['Date'])
    historico_ativo.set_index('Date', inplace=True)

    # Calcular a valorização mensal desde o início do mês
    df_monthly_start = historico_ativo['Close'].resample('MS').first()
    df_monthly_return = round(df_monthly_start.pct_change() * 100, 2)

    # Exibir o DataFrame resultante
    # return df_monthly_return
    df = pd.DataFrame({'data': pd.to_datetime(df_monthly_start.index), 'variacao_%': df_monthly_return.tolist(), 'codigo_ativo': ativo})
    
    df['variacao_acumulada_%'] = df['variacao_%'].cumsum()
    # df.drop(index=0) pois o primeiro registro da variação é NaN
    return df.drop(index=0)

def transform_valores_eventos(df):
    """
        Realiza a transformação dos valores com base nas atividade de evento
        Retorna os valores transformados dependendo se o ativo foi comprado ou vendido
    """
    # TODO: Se uma pessoa compra e vende varios ativos ao longo desse tempo quanto ela faturou?

    df['quantidade'] *= df['evento'].map({'Compra': 1, 'Venda': -1}).fillna(0)
    df['valor_compra'] *= df['evento'].map({'Compra': 1, 'Venda': -1}).fillna(0)

    resultado = df.groupby('codigo_ativo')[['quantidade', 'valor_compra']].sum().reset_index()
    
    resultado['carteira_%'] = (resultado['valor_compra'] / resultado['valor_compra'].sum()) * 100
    resultado['carteira_%'] = resultado['carteira_%'].apply(lambda x: round(x, 2))

    return resultado

def generate_portfolio_report_reduced(df_transaction_history):
    list_ativos = df_transaction_history['codigo_ativo'].unique()

    for ativo in list_ativos:
        custo_medio = calcular_custo_medio(df_transaction_history=df_transaction_history, ativo=ativo)

def get_generate_portfolio_report(df_transaction_history):
    """
    Gera o portfolio da sua carteira de ações
    """

    df_transaction_history = df_transaction_history.copy()
    list_ativos = get_ativos_in_carteira(df_transaction_history)

    # Removendo ativos que não estão em carteira]
    df_transaction_history = df_transaction_history[df_transaction_history['codigo_ativo'].isin(list_ativos)]
    # list_ativos = df_historico_dividendos['codigo_ativo'].unique()

    list_relatorio = []
    
    for ativo in list_ativos:
        resultado_anual = analise_anual_dividendos_fii(ativo=ativo)
        df_historic_DY_emojis = historic_DY_emojis(ativo=ativo)
        variacao_percentual_mensal = calcular_variacao_percentual_mensal(ativo)

        dict_relatorio = {'codigo_ativo': ativo,
                          'DY_anual_%': round(resultado_anual['DY_anual_%'].item(), 2),
                          'yield_on_cost_anual_%': round(resultado_anual['yield_on_cost_anual_%'].item(), 2),
                          'recebidos_por_cota_anual': round(resultado_anual['recebidos_por_cota_anual'].item(), 2),
                           'historic_DY_emojis_meses': df_historic_DY_emojis['historic_DY_emojis_meses'].item(),
                          'variacao_percentual_mensal': variacao_percentual_mensal['variacao_%'].tolist(),
                          'variacao_acumulada_%': variacao_percentual_mensal['variacao_%'].sum()
                          }
        
        info_ativos_pagos = info_dividendos_pagos(ativo=ativo)
        dict_relatorio.update(info_ativos_pagos)

        custo_medio = calcular_custo_medio(df_transaction_history=df_transaction_history, ativo=ativo)
        dict_relatorio.update(custo_medio)

        list_relatorio.append(dict_relatorio)
        


    df_info_ativos = pd.DataFrame(list_relatorio)
    
    valores_eventos_transform = transform_valores_eventos(df_transaction_history)

    df_info_ativos = pd.merge(df_info_ativos, valores_eventos_transform, on='codigo_ativo', how='left')

    #df_variacao_ativo = calc_variacao(df_info_ativos)
    #df_info_ativos = pd.merge(df_info_ativos, df_variacao_ativo, on='codigo_ativo', how='left')
    

    # Realiza o calculo afim de verificar qual a porcentagem da valorização entre o valor 
    #    dos ativos que foram comprados Vs o valor dos ativos atualmente
    patrimonio_atual = df_info_ativos['quantidade']*df_info_ativos['valor_unitario_atualizado']
    valorizacao_patrimonio = ((patrimonio_atual * 100) / df_info_ativos['valor_compra']) - 100
    df_info_ativos['patrimonio_atual_R$'] = round(patrimonio_atual, 2) 
    df_info_ativos['valorizacao_patrimonio_%'] = valorizacao_patrimonio.apply(lambda x: f"{x:.2f}")
    df_info_ativos['minha_nota'] = 0
    df_info_ativos['ideal_%'] = 0
    df_info_ativos['comprar_?'] = 'sim'

    # 

    return df_info_ativos.sort_values(by=['DY_anual_%', 'yield_on_cost_anual_%'], ascending=False)

# Criar uma função para calcular a variação, ignorando divisões por zero

def calc_variacao(df_info_ativos):
    """
    Realiza o cálculo da variação do ativo em porcentagem.
    :param df_info_ativos: DataFrame com informações dos ativos.
    :return: DataFrame com código do ativo e variação percentual.
    """

    def calcular_variacao(antigo, atual):
        if antigo == 0:
            return 0  # Ou outro valor padrão, como NaN ou uma string para indicar erro
        else:
            return round(((atual - antigo) / antigo) * 100, 2)
        
    df = df_info_ativos[['codigo_ativo', 'quantidade', 'custo_medio', 'valor_unitario_atualizado']].copy()
    
    # Cálculo do patrimônio antigo e atual
    valor_patrimonio_antigo = df['quantidade'] * df['custo_medio']
    valor_patrimonio_atual = df['quantidade'] * df['valor_unitario_atualizado'] 

    # Aplicar a função de forma vetorizada no DataFrame
    df['variacao_ativo_%'] = [calcular_variacao(antigo, atual) for antigo, atual in zip(valor_patrimonio_antigo, valor_patrimonio_atual)]


    return df[['codigo_ativo', 'variacao_ativo_%']]