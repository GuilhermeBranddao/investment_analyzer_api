from fastapi import APIRouter
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

from app.routers.dependencies import get_current_user

router = APIRouter()

# Configurações para JWT
SECRET_KEY = 'caa9c8f8620cbb30679026bb6427e11f'
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 3000

@router.post("/signup")
def signup(user: User, session: Session = Depends(get_db)):
    repository_user = RepositoryUser(session)

    if repository_user.get_user_per_email(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um usuário para este e-mail",
        )

    user.password = gerar_hash(user.password)
    return repository_user.create_user(user)


@router.post("/token", response_model=dict)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_db)
):
    repository_user = RepositoryUser(session)
    user = repository_user.get_user_per_email(form_data.username)

    if not user or not verificar_hash(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha estão incorretos!",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = criar_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

