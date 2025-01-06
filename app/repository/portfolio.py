from sqlalchemy import select
from app.schemas.portfolio import Portfolio, AssetTransaction, AssetPriceHistory
from sqlalchemy.exc import NoResultFound
from app.models import models 
from app.models.models import Asset
from typing import List

from datetime import datetime
from typing import Optional

class RepositoryPortfolio():
    def __init__(self, session):
        self.session = session

    def create_portfolio(self, portfolio: Portfolio):
        portfolio_model = models.Portfolio(
            name = portfolio.name,
            user_id = portfolio.user_id,
            description = portfolio.description,
        )

        self.session.add(portfolio_model)
        self.session.commit()
        self.session.refresh(portfolio_model)
        return portfolio_model
    
    def check_exist_asset(self, asset_id:int):
        asset_data = select(models.Asset).where(
            models.Asset.id == asset_id)
        return self.session.execute(asset_data).scalars().first() 

    def portfolio_belongs_user(self):
        pass
        
    def get_asset_transaction(self, portfolio_id:int):
        transaction_data = select(models.AssetTransaction).where(
            models.AssetTransaction.portfolio_id == portfolio_id)
        
        return self.session.execute(transaction_data).scalars().all() 

    def add_asset_transaction(self, asset_transaction:AssetTransaction):
        """
        Cria uma transação e registra o ativo se ele não existir.
        """

        # Verificar se o asset_id existe
        asset_transaction_model = models.AssetTransaction(
            quantity = asset_transaction.quantity,
            unit_value = asset_transaction.unit_value,
            purchase_value = asset_transaction.purchase_value,
            date = asset_transaction.date,
            portfolio_id = asset_transaction.portfolio_id,
            transaction_type_id = asset_transaction.transaction_type_id,
            asset_id = asset_transaction.asset_id,
        )
        
        self.session.add(asset_transaction_model)
        self.session.commit()
        self.session.refresh(asset_transaction_model)
        return asset_transaction_model
    

    def portfolio_infos(self, portfolio_id) -> List[AssetTransaction]:
        transaction_data = select(models.AssetTransaction).where(
            models.AssetTransaction.portfolio_id == portfolio_id)
        
        transactions = self.session.execute(transaction_data).scalars().all()
        # Converte os objetos SQLAlchemy em modelos Pydantic
        result = [AssetTransaction.model_validate(transaction).model_dump() for transaction in transactions]
        
        return result
    
    def get_asset_id_per_name(self, asset_name):
        asset_data = select(models.Asset).where(
            models.Asset.symbol == asset_name)
        
        asset_first = self.session.execute(asset_data).scalars().first()

        if asset_first:
            return asset_first.id

        return None
    
    def get_asset_name_per_id(self, asset_id):
        asset_data = select(models.Asset).where(
            models.Asset.id == asset_id)
        
        asset_first = self.session.execute(asset_data).scalars().first()

        if asset_first:
            return asset_first.symbol

        return None
    
    def get_transaction_type_name_per_id(self, transaction_type_id):
        transaction_type_data = select(models.TransactionType).where(
            models.TransactionType.id == transaction_type_id
        )

        transaction_type_first = self.session.execute(transaction_type_data).scalars().first()

        if transaction_type_first:
            return transaction_type_first.type_name

        return None
        

    def history(self, asset_id: int, start: Optional[datetime] = None, end: Optional[datetime] = None):
        # Construindo a consulta com filtros opcionais de data
        query = select(models.AssetPriceHistory).where(
            models.AssetPriceHistory.asset_id == int(asset_id))

        if start:
            query = query.where(models.AssetPriceHistory.date >= start)
        if end:
            query = query.where(models.AssetPriceHistory.date <= end)

        # Executando a consulta
        asset_price_history_data = self.session.execute(query).scalars().all()

        # Validando os dados com Pydantic e retornando como dicionário
        result = [
            AssetPriceHistory.model_validate(record).model_dump() 
            for record in asset_price_history_data
        ]
        
        return result