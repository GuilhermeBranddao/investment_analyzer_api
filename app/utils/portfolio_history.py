import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict
from app.models import models 


def generate_date_range(start_date: str, end_date: str) -> list:
    """
    Gera uma lista de datas no formato ISO8601 (`YYYY-MM-DDTHH:mm:ss`)
    entre a data inicial e a data final.

    Args:
        start_date (str): Data inicial no formato ISO8601.
        end_date (str): Data final no formato ISO8601.

    Returns:
        list: Lista de strings representando as datas no intervalo.
    """
    start = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S") if isinstance(start_date, str) else start_date 
    end = datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S") if isinstance(end_date, str) else end_date 

    delta = timedelta(days=1)
    return [
        (start + i * delta)#.strftime("%Y-%m-%dT%H:%M:%S")
        for i in range((end - start).days + 1)
    ]


def group_transactions_by_asset(transactions: models.AssetTransaction) -> dict:
    """
    Agrupa as transações por `asset_id`.

    Args:
        transactions (list): Lista de transações.

    Returns:
        dict: Dicionário com o `asset_id` como chave e as transações como valores.
    """
    grouped_transactions = defaultdict(list)
    for transaction in transactions:
        grouped_transactions[transaction.asset_id].append(transaction)
    return grouped_transactions


def build_asset_history(asset_id: int, transactions: models.AssetTransaction, end_date: str) -> list:
    """
    Gera o histórico diário de um ativo, acumulando quantidade e valor.

    Args:
        asset_id (int): Identificador do ativo.
        transactions (list): Lista de transações do ativo.
        end_date (str): Data final do histórico no formato ISO8601.

    Returns:
        list: Histórico diário do ativo com `date`, `quantity`, `purchase_value` e `user_asset_value`.
    """
    # Ordena as transações por data
    transactions = sorted(transactions, key=lambda x: x.date)

    # Define o intervalo de datas
    first_date = transactions[0].date
    date_range = generate_date_range(first_date, end_date)

    # Inicializa o histórico com datas
    history = [{"date": date, 
                "asset_id": asset_id, 
                "quantity": 0,
                'purchase_value': 0,
                "user_asset_value": 0,
                "transaction_type_id":"-",
                "unit_value":"-"} for date in date_range]

    # Acumula os valores com base nas transações
    quantity = 0
    user_asset_value = 0
    purchase_value = 0
    for transaction in transactions:
        if transaction.transaction_type_id == 0:  # Compra
            quantity += transaction.quantity
            purchase_value += transaction.purchase_value
        else:  # Venda
            quantity -= transaction.quantity
            purchase_value -= transaction.purchase_value

        
        # Atualiza o histórico a partir da data da transação
        for entry in history:
            if entry["date"] == transaction.date:
                entry["transaction_type_id"] = transaction.transaction_type_id
                entry["unit_value"] = transaction.unit_value
            if entry["date"] >= transaction.date:
                entry["quantity"] = quantity
                entry["purchase_value"] = purchase_value

    return history


def generate_portfolio_history(transactions: models.AssetTransaction, end_date: str = None) -> list:
    """
    Gera o histórico diário para todos os ativos de um portfólio.

    Args:
        transactions (list): Lista de transações.
        end_date (str, optional): Data final do histórico no formato ISO8601.
                                  Se não especificado, usa a data atual.

    Returns:
        list: Histórico diário consolidado para todos os ativos.
    """
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    # Agrupa as transações por ativo
    grouped_transactions = group_transactions_by_asset(transactions)

    # Gera o histórico para cada ativo
    history = []
    for asset_id, asset_transactions in grouped_transactions.items():
        asset_history = build_asset_history(asset_id, asset_transactions, end_date)
        history.extend(asset_history)

    return history

def merge_with_history(portfolio_history: pd.DataFrame, df_history: pd.DataFrame) -> pd.DataFrame:
    """
    Mescla o histórico do portfólio com os dados de mercado do ativo.

    Args:
        portfolio_history (pd.DataFrame): Histórico diário do portfólio.
        df_history (pd.DataFrame): Dados de mercado do ativo.

    Returns:
        pd.DataFrame: DataFrame mesclado com o histórico do portfólio e os dados de mercado.
    """
    # Conversão de datas para datetime
    portfolio_history["date"] = pd.to_datetime(portfolio_history["date"])
    df_history["date"] = pd.to_datetime(df_history["date"])

    # Remove a coluna 'asset_id' dos dados de mercado para evitar duplicações
    #df_history = df_history.drop(columns=["asset_id"], errors="ignore")

    # Mescla os dois DataFrames
    merged_data = pd.merge(portfolio_history, df_history, on=["date", "asset_id"], how="left")

    # Remove registros sem dados de mercado
    merged_data.dropna(subset=["open", "high", "close"], inplace=True)

    # Calcula o valor do ativo com base na quantidade e no preço de fechamento
    merged_data["user_asset_value"] = merged_data["quantity"] * merged_data["close"]

    return merged_data
