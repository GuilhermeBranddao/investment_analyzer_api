from datetime import datetime, timedelta
from jose import jwt
from app.settings.config import Settings

settings = Settings()


def criar_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": int(expire.timestamp())})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verificar_access_token(token: str):
    carga = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    return carga.get('sub')