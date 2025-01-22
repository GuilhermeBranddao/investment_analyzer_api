from sqlalchemy import select
from app.schemas.portfolio import Portfolio, AssetTransaction, AssetPriceHistory
from sqlalchemy.exc import NoResultFound
from app.models import models 
from app.models.models import Asset
from typing import List

from datetime import datetime, timedelta

from typing import Optional, Union

import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from functools import partial

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
    
    def asset_transaction_edit(self, asset_transaction: AssetTransaction):
        try:
            # Recupera a transação de ativo do banco de dados pelo ID
            transaction_query = select(models.AssetTransaction).where(models.AssetTransaction.id == asset_transaction.id)
            transaction = self.session.execute(transaction_query).scalar_one()

            # Atualiza os campos da transação de ativo com base nos dados fornecidos
            if asset_transaction.quantity is not None:
                transaction.quantity = asset_transaction.quantity
            
            if asset_transaction.unit_value is not None:
                transaction.unit_value = asset_transaction.unit_value
            
            if asset_transaction.purchase_value is not None:
                transaction.purchase_value = asset_transaction.purchase_value
            
            if asset_transaction.date is not None:
                transaction.date = asset_transaction.date
            
            if asset_transaction.portfolio_id is not None:
                transaction.portfolio_id = asset_transaction.portfolio_id
            
            if asset_transaction.transaction_type_id is not None:
                transaction.transaction_type_id = asset_transaction.transaction_type_id
            
            if asset_transaction.asset_id is not None:
                transaction.asset_id = asset_transaction.asset_id

            # Atualiza os dados no banco de dados
            self.session.commit()
            self.session.refresh(transaction)

            return transaction

        except NoResultFound:
            raise ValueError(f"Asset transaction with ID {asset_transaction.id} not found.")


    
    def check_exist_portfolio_name_duplicate(self, portfolio_name:str, user_id:int):
        portfolio_data = select(models.Portfolio).where((models.Portfolio.name == portfolio_name) & (models.Portfolio.user_id == user_id))
        
        return self.session.execute(portfolio_data).scalars().first()

    def list_portfolios(self, user_id:int):
        portfolio_data = select(models.Portfolio).where(
            models.Portfolio.user_id == user_id)
        return self.session.execute(portfolio_data).scalars().all()
    
    def list_assets(self):
        asset_data = select(models.Asset)
        return self.session.execute(asset_data).scalars().all()

    def check_exist_asset(self, asset_id:int):
        asset_data = select(models.Asset).where(
            models.Asset.id == asset_id)
        return self.session.execute(asset_data).scalars().first() 

    def check_exist_transaction(self, transaction_id: int):
        """
        Verifica se uma transação com o ID fornecido existe na base de dados.

        Args:
            transaction_id (int): ID da transação.

        Returns:
            bool: True se a transação existe, False caso contrário.
        """
        transaction_data = select(models.AssetTransaction).where(
            models.AssetTransaction.id == transaction_id
        )
        return self.session.execute(transaction_data).scalars().first()
    
    def check_exist_wallet(self, wallet_id: int):
        """
        Verifica se uma carteira com o ID fornecido existe na base de dados.

        Args:
            wallet_id (int): ID da carteira.

        Returns:
            bool: True se a carteira existe, False caso contrário.
        """
        wallet_data = select(models.Portfolio).where(
            models.Portfolio.id == wallet_id
        )
        return self.session.execute(wallet_data).scalars().first()

    def delete_wallet(self, wallet_id: int):
        """
        Deleta uma carteira com base no ID.

        Args:
            wallet_id (int): ID da carteira a ser deletada.
        """
        wallet = self.check_exist_wallet(wallet_id)
        if wallet:
            self.session.delete(wallet)
            self.session.commit()

    def delete_asset_transaction(self, transaction_id: int):
        """
        Deleta uma transação com base no ID.

        Args:
            transaction_id (int): ID da transação a ser deletada.
        """
        transaction = self.check_exist_transaction(transaction_id)
        if transaction:
            self.session.delete(transaction)
            self.session.commit()
        
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

    def get_asset_transaction_per_id(self, asset_transaction_id:int) -> dict:
        query = select(models.AssetTransaction).where(
            models.AssetTransaction.id == asset_transaction_id)
        
        asset_transaction = self.session.execute(query).scalars().first()
        return asset_transaction
    
    def history(
            self, 
            assets_id: Union[int, set[int]], 
            start: Optional[datetime] = None, 
            end: Optional[datetime] = None
        ) -> list[dict]:
        """
        Retorna o histórico de preços de um ou mais ativos dentro de um intervalo de datas opcional.

        Args:
            assets_id (Union[int, set[int]]): ID do ativo ou conjunto de IDs.
            start (Optional[datetime]): Data inicial do intervalo (inclusiva).
            end (Optional[datetime]): Data final do intervalo (inclusiva).

        Returns:
            list[dict]: Lista de registros do histórico de preços, validados e formatados como dicionários.
        """
        # Converte assets_id para set se for int
        asset_ids = {assets_id} if isinstance(assets_id, int) else set(assets_id)

        # Construção da consulta base
        query = select(models.AssetPriceHistory).where(
            models.AssetPriceHistory.asset_id.in_(asset_ids)
        )

        # Adiciona filtros opcionais de data, se fornecidos
        if start:
            query = query.where(models.AssetPriceHistory.date >= start)
        if end:
            query = query.where(models.AssetPriceHistory.date <= end)

        # Executa a consulta no banco de dados com otimização de índices
        asset_price_history_data = self.session.execute(query).fetchall()

        # Valida os dados retornados e converte para formato dicionário
        return [
            AssetPriceHistory.model_validate(record[0]).model_dump()
            for record in asset_price_history_data
        ]
       
    
    def history_by_asset(self, asset_id: int, start: Optional[datetime] = None, end: Optional[datetime] = None):
        """
        Retorna o histórico de preços de um único ativo dentro de um intervalo de datas.

        Args:
            asset_id (int): ID do ativo.
            start (Optional[datetime]): Data inicial do intervalo (inclusiva).
            end (Optional[datetime]): Data final do intervalo (inclusiva).

        Returns:
            list[dict]: Lista de registros do histórico de preços, validados e formatados como dicionários.
        """

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
    
