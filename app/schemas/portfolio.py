from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AssetTransaction(BaseModel):
    id: Optional[int] = None
    quantity: int
    unit_value: float
    purchase_value: float
    date: datetime
    portfolio_id: int
    transaction_type_id: Optional[int] = 1
    asset_id: int

    class Config:
        from_attributes = True 

class Portfolio(BaseModel):
    id: Optional[int] = None
    name: str
    user_id: Optional[int] = None
    description: Optional[int] = None

class AssetPriceHistory(BaseModel):
    id: Optional[int] = None
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    dividends: float
    stock_splits: float
    asset_id: int

    class Config:
        from_attributes = True 