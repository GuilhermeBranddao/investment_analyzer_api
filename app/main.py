from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import timedelta, datetime
from jose import JWTError, jwt
from typing import Annotated

from app.schemas.schemas import User, LoginData, UserBasic
from app.schemas.portfolio import Portfolio, AssetTransaction
from app.infra.config.database import get_db
from app.repository.auth import RepositoryUser
from app.repository.portfolio import RepositoryPortfolio
from app.infra.providers.hash_provider import gerar_hash, verificar_hash
from app.infra.providers.token_provider import criar_access_token, verificar_access_token
from app.routers import auth, portfolio
from app.routers.dependencies import get_current_user
from app.settings.config import Settings
from app.infra.initialize_database import initialize_database
from app.models.models import *
from app.infra.config.database import get_session_local, create_all_tables, create_engine_db
# Inicialização do FastAPI
app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
settings = Settings()

# Inicializando tabelas
initialize_database.feeds_main(session=get_session_local())
create_all_tables(engine=create_engine_db(DATABASE_URL=settings.DATABASE_URL), 
                  Base=Base)

app.include_router(auth.router, prefix='/auth', tags=['auth'])
app.include_router(portfolio.router, prefix='/portfolio', tags=['portfolio'])






