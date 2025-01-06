from fastapi import APIRouter
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated

from app.schemas.schemas import UserBasic
from app.schemas.portfolio import Portfolio, AssetTransaction
from app.infra.config.database import get_db
from app.repository.portfolio import RepositoryPortfolio
from app.routers.dependencies import get_current_user

router = APIRouter()

@router.post("/create")
def create_portfolio(portfolio: Portfolio, 
                     current_user: Annotated[UserBasic, Depends(get_current_user)],
                     session: Session = Depends(get_db)):
    
    repository_portfolio = RepositoryPortfolio(session)

    portfolio.user_id = current_user.id
    return repository_portfolio.create_portfolio(portfolio)


@router.post("/transaction")
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

from app.PortfolioManager.utils.auxiliary_functions import repository_portfolio_manage
from app.PortfolioManager.calculations.assets import calculate_portfolio_value_optimized
from app.PortfolioManager.calculations.dividends_received_history import dividends_received_history
import pandas as pd

@router.get("/transaction/history/{portfolio_id}")
def get_transaction_history(portfolio_id:int):
    repository_portfolio = repository_portfolio_manage()
    transaction_history = repository_portfolio.portfolio_infos(portfolio_id=portfolio_id)
    df_transaction_history = pd.DataFrame(transaction_history)
    df_transaction_history =  calculate_portfolio_value_optimized(df_transaction_history)
    return df_transaction_history.to_dict("records")

@router.get("/dividends-received-history/{portfolio_id}")
def get_dividends_received_history(portfolio_id: int):
    repository_portfolio = repository_portfolio_manage()
    transaction_history = repository_portfolio.portfolio_infos(portfolio_id=portfolio_id)
    df_transaction_history = pd.DataFrame(transaction_history)
    df_transaction_history =  calculate_portfolio_value_optimized(df_transaction_history)
    df_historico_dividendos =  dividends_received_history(df_transaction_history=df_transaction_history)
    return df_historico_dividendos.to_dict("records")


