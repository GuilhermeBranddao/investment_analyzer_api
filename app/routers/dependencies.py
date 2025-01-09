# app/routers/dependencies.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from app.infra.providers.token_provider import verificar_access_token
from app.repository.auth import RepositoryUser
from app.schemas.schemas import UserBasic
from app.infra.config.database import get_db
from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

async def get_current_user(
    token: str = Depends(oauth2_scheme), session: Session = Depends(get_db)
):
    try:
        email = verificar_access_token(token)
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas!",
                headers={"WWW-Authenticate": "Bearer"},
            )

        repository_user = RepositoryUser(session)
        user = repository_user.get_user_per_email(email)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas!",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return UserBasic(id=user.id, name=user.name, email=user.email)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido!",
            headers={"WWW-Authenticate": "Bearer"},
        )
