from sqlalchemy import create_engine, Column, Integer, String, select, insert, exists
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.models.models import TransactionType, Status
from sqlalchemy.orm import Session
from app.schemas.constants.enums import TransactionTypeEnum, StatusEnum

# Base declarativa
Base = declarative_base()


def feeds_main(session:Session):
    feeds_status_table(session)
    feeds_transaction_type_table(session)

def feeds_status_table(session:Session):
    initial_data = [
        {"id": StatusEnum.ADMIN_ID.value, "name": StatusEnum.ADMIN_NAME.value},
        {"id": StatusEnum.USER_ID.value, "name": StatusEnum.USER_NAME.value}
    ]

    for data in initial_data:
        exists_query = session.query(exists().where(Status.id == data["id"])).scalar()
        if not exists_query:
            session.add(Status(**data))


# Função para criar e popular a tabela
def feeds_transaction_type_table(session:Session):
    initial_data = [
        {"id": TransactionTypeEnum.COMPRA_ID.value, "type_name": TransactionTypeEnum.COMPRA_NAME.value},
        {"id": TransactionTypeEnum.VENDA_ID.value, "type_name": TransactionTypeEnum.VENDA_NAME.value}
    ]

    for data in initial_data:
        exists_query = session.query(exists().where(TransactionType.id == data["id"])).scalar()
        if not exists_query:
            session.add(TransactionType(**data))

    

    # Confirmar alterações
    session.commit()
    session.close()
