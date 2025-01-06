from datetime import datetime, timedelta
from jose import jwt

# CONFIG
SECRET_KEY = 'caa9c8f8620cbb30679026bb6427e11f'
ALGORITHM = 'HS256'
EXPIRES_IN_MIN = 3000


def criar_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verificar_access_token(token: str):
    carga = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return carga.get('sub')