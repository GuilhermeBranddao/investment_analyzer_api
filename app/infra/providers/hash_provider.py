from passlib.context import CryptContext

# pwd_context = CryptContext(schemes=['bcrypt'])
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def gerar_hash(password):
    hashed_password = pwd_context.hash(password)
    return hashed_password


def verificar_hash(password, hash):
    return pwd_context.verify(password, hash)