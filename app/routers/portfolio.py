from fastapi import APIRouter
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated

from app.schemas.schemas import UserBasic
from app.schemas.portfolio import Portfolio, AssetTransaction
from app.infra.config.database import get_db
from app.repository.portfolio import RepositoryPortfolio
from app.routers.dependencies import get_current_user
from datetime import datetime, timedelta
from typing import Any


router = APIRouter()

@router.post("/create")
def create_portfolio(portfolio: Portfolio, 
                     current_user: Annotated[UserBasic, Depends(get_current_user)],
                     session: Session = Depends(get_db)):
    
    repository_portfolio = RepositoryPortfolio(session)

    if repository_portfolio.check_exist_portfolio_name_duplicate(portfolio.name, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Você já possui uma carteira com este nome!",
        )

    portfolio.user_id = current_user.id
    return repository_portfolio.create_portfolio(portfolio)

@router.get("/list")
def list_portfolios(current_user: Annotated[UserBasic, Depends(get_current_user)],
                    session: Session = Depends(get_db)):
    
    repository_portfolio = RepositoryPortfolio(session)
    return repository_portfolio.list_portfolios(current_user.id)

@router.post("/transaction/add")
def add_transaction(transaction: AssetTransaction, session: Session = Depends(get_db)):
    repository_portfolio = RepositoryPortfolio(session)

    if not repository_portfolio.check_exist_asset(transaction.asset_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ativo {transaction.asset_id} não existe na base de dados!",
        )

    return repository_portfolio.add_asset_transaction(transaction)

@router.get("/transaction/{portfolio_id}")
def get_transaction(portfolio_id:int, session: Session = Depends(get_db)):

    # TODO: Verificar se portfolio pertence ao usuario
    repository_portfolio = RepositoryPortfolio(session)
    transaction_data = repository_portfolio.get_asset_transaction(portfolio_id)

    return transaction_data

from app.utils.portfolio_history import generate_portfolio_history, merge_with_history
import json
@router.get("/history/{portfolio_id}")
def get_portfolio_history(portfolio_id:int, session: Session = Depends(get_db)):
    repository_portfolio = RepositoryPortfolio(session)
    

    # TODO: Verifica se portfolio existe
    transaction_data = repository_portfolio.get_asset_transaction(portfolio_id)
    portfolio_history = generate_portfolio_history(transaction_data)
    set_asset_id = {transaction['asset_id'] for transaction in portfolio_history}
    df_portfolio_history = pd.DataFrame(portfolio_history)
    all_history = repository_portfolio.history(set_asset_id)
    df_history = pd.DataFrame(all_history)
    merged_data = merge_with_history(df_portfolio_history, df_history)
    merged_data["date"] = merged_data["date"].astype(str)
    data = json.loads(merged_data.to_json(orient="records"))
    return data


@router.get("/asset/list")
def list_assets(session: Session = Depends(get_db)):
    repository_portfolio = RepositoryPortfolio(session)
    data = repository_portfolio.list_assets()
    return data

from app.PortfolioManager.utils.auxiliary_functions import repository_portfolio_manage
from app.PortfolioManager.calculations.assets import calculate_portfolio_value_optimized
from app.PortfolioManager.calculations.dividends_received_history import dividends_received_history
import pandas as pd

@router.get("/transaction/history/{portfolio_id}")
def get_transaction_history(portfolio_id:int):
    repository_portfolio = repository_portfolio_manage()
    transaction_history = repository_portfolio.portfolio_infos(portfolio_id=portfolio_id)
    if not transaction_history:
        return {}
    df_transaction_history = pd.DataFrame(transaction_history)
    df_transaction_history = calculate_portfolio_value_optimized(df_transaction_history)
    return df_transaction_history.to_dict("records")

@router.get("/dividends-received-history/{portfolio_id}")
def get_dividends_received_history(portfolio_id: int):
    repository_portfolio = repository_portfolio_manage()
    transaction_history = repository_portfolio.portfolio_infos(portfolio_id=portfolio_id)
    df_transaction_history = pd.DataFrame(transaction_history)
    df_transaction_history =  calculate_portfolio_value_optimized(df_transaction_history)
    df_historico_dividendos =  dividends_received_history(df_transaction_history=df_transaction_history)
    return df_historico_dividendos.to_dict("records")

@router.get("/get-asset-transaction/{asset_transaction_id}")
def get_asset_transaction_per_id(asset_transaction_id: int, session: Session = Depends(get_db)):
    # Inicializar o repositório
    repository_portfolio = RepositoryPortfolio(session)

    asset_transaction = repository_portfolio.get_asset_transaction_per_id(asset_transaction_id=asset_transaction_id)

    return asset_transaction

@router.put("/asset-transaction/edit")
def asset_transaction_edit(asset_transaction: AssetTransaction,
                     session: Session = Depends(get_db)):
    
    repository_portfolio = RepositoryPortfolio(session)

    # TODO: verificar se essa transação pertence ao usuario
    #if repository_portfolio.check_exist_portfolio_name_duplicate(asset_transaction.id, current_user.id):
    #    raise HTTPException(
    #        status_code=status.HTTP_400_BAD_REQUEST,
    #        detail=f"Você já possui uma carteira com este nome!",
    #    )
    #portfolio.user_id = current_user.id

    return repository_portfolio.asset_transaction_edit(asset_transaction)


@router.get("/get-price-class/")
def get_close_per_date_and_asset_id(
    asset_id: int,
    date: str,
    session: Session = Depends(get_db),
) -> Any:
    """
    Retorna a média dos valores de fechamento (close) de 5 dias ao redor da data fornecida.

    Args:
        asset_id (int): ID do ativo.
        date (str): Data fornecida pelo usuário (no formato 'YYYY-MM-DD').
        session (Session): Sessão do banco de dados (injetada pelo FastAPI).

    Returns:
        dict: Média dos valores de fechamento (close) no intervalo de 5 dias.
    """
    try:
        # Inicializar o repositório
        repository_portfolio = RepositoryPortfolio(session)

        # Validar o formato da data
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"A data '{date}' não está no formato válido (YYYY-MM-DD).",
            )

        # Definir o intervalo de 5 dias
        start_date = target_date - timedelta(days=2)
        end_date = target_date + timedelta(days=2)

        # Obter o histórico de preços do ativo no intervalo
        price_history = repository_portfolio.history_by_asset(
            asset_id=asset_id, start=start_date, end=end_date
        )

        # Verificar se há registros no intervalo
        if not price_history:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"Nenhum dado de histórico encontrado para o ativo {asset_id} "
                    f"no intervalo de {start_date.date()} a {end_date.date()}."
                ),
            )

        # Calcular a média dos valores de fechamento (close)
        close_values = [record["close"] for record in price_history]
        close_average = sum(close_values) / len(close_values)

        # Retornar uma resposta estruturada
        return {
            "asset_id": asset_id,
            "date": date,
            "average_close": close_average,
            "start_date": start_date.date().isoformat(),
            "end_date": end_date.date().isoformat(),
            "records_count": len(close_values),
        }

    except HTTPException as e:
        # Re-levantar exceções HTTP para o FastAPI
        raise e
    except Exception as e:
        # Capturar erros inesperados
        raise HTTPException(
            status_code=500,
            detail=f"Ocorreu um erro inesperado: {str(e)}",
        )

