from fastapi import APIRouter
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from app.schemas.schemas import User
from app.infra.config.database import get_db
from app.repository.auth import RepositoryUser
from app.infra.providers.hash_provider import gerar_hash, verificar_hash
from app.infra.providers.token_provider import criar_access_token

from app.validation.password_validation import validate_password
from app.validation.email_validation import validate_email
from app.validation.name_validation import validate_name
from app.settings.config import Settings

settings = Settings()
router = APIRouter()

@router.post("/signup")
def signup(user: User, session: Session = Depends(get_db)):
    repository_user = RepositoryUser(session)

    validate_name(name=user.name)
    validate_email(user_email=user.email,
                   repository_user=repository_user)
    validate_password(user_password=user.password,
                      username=user.name)


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

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = criar_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

