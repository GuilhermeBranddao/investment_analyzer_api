from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer

from app.routers import auth, portfolio
from app.settings.config import Settings
from app.models.models import Base
from app.infra.config.database import create_all_tables, create_engine_db

# Inicialização do FastAPI
app = FastAPI()

# `OAuth2PasswordBearer` espera o token no cabeçalho Authorization Ex: "Authorization: Bearer <token>""
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
settings = Settings()

# Inicializando tabelas
#initialize_database.feeds_main(session=get_session_local())

create_all_tables(engine=create_engine_db(DATABASE_URL=settings.DATABASE_URL), 
                  Base=Base)

app.include_router(auth.router, prefix='/auth', tags=['auth'])
app.include_router(portfolio.router, prefix='/portfolio', tags=['portfolio'])






