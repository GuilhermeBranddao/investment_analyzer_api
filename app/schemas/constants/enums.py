from enum import Enum

class TransactionTypeEnum(Enum):
    COMPRA_NAME = "Compra"
    VENDA_NAME = "Venda"
    COMPRA_ID = 0
    VENDA_ID = 1

class StatusEnum(Enum):
    ADMIN_NAME = "Admin"
    USER_NAME = "User"
    ADMIN_ID = 0
    USER_ID = 1

