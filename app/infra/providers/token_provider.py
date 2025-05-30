from datetime import datetime, timedelta
from jose import jwt
from app.settings.config import Settings
from jose import jwt, JWTError, ExpiredSignatureError

settings = Settings()


def criar_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": int(expire.timestamp())})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verificar_access_token(token: str | None) -> str | None:
    """
    Verifica e decodifica um access token JWT, retornando o 'subject' (sub).

    Args:
        token: O access token JWT como uma string, ou None.

    Returns:
        O valor da claim 'sub' (subject) se o token for válido, não expirado,
        corretamente assinado e contiver a claim 'sub'.
        Retorna None caso contrário (token inválido, erro na decodificação,
        'sub' ausente, etc.).
    """
    # 1. Validação da Entrada do Token
    #    Certifique-se de que o token não é None, uma string vazia ou de tipo incorreto
    #    antes de tentar decodificá-lo. Este é um ponto crucial para evitar o erro
    #    de 'rsplit' que vimos anteriormente se 'token' for None ou não for uma string.
    if not token or not isinstance(token, str):
        # print(f"DEBUG: Token inválido fornecido para verificação: {token}") # Para depuração
        return None

    try:
        # 2. Decodificação e Verificação
        #    A função jwt.decode fará as seguintes verificações:
        #    - Formato do JWT
        #    - Validade da assinatura (usando settings.SECRET_KEY e settings.ALGORITHM)
        #    - Expiração do token (claim 'exp')
        #    - Outras claims de tempo padrão (nbf, iat) se presentes e options não as desabilitarem
        carga_decodificada = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
            # Você pode adicionar 'options' aqui se precisar de verificações mais finas,
            # por exemplo, para ignorar a verificação de expiração (não recomendado para access tokens):
            # options={"verify_exp": False}
        )

        # 3. Extração da Claim 'sub'
        #    O método .get('sub') retorna o valor da claim 'sub' se existir,
        #    ou None se não existir, o que é um comportamento seguro.
        return carga_decodificada.get('sub')

    # 4. Tratamento de Erros Específicos do JWT
    except ExpiredSignatureError:
        # print(f"DEBUG: Token JWT expirou: {token[:30]}...") # Para depuração
        # Token expirou. Você pode logar isso ou tratar de forma específica.
        return None
    except JWTError as e:
        # JWTError é uma classe base para muitas outras exceções da biblioteca jose
        # (ex: InvalidClaimError, InvalidAudienceError, etc.).
        # print(f"DEBUG: Erro JWT ao decodificar token: {e} - Token: {token[:30]}...") # Para depuração
        return None
    except Exception as e:
        # Captura genérica para qualquer outro erro inesperado durante o processo.
        # É uma boa prática logar esse tipo de erro.
        # print(f"DEBUG: Erro inesperado ao verificar token: {e} - Token: {token[:30]}...") # Para depuração
        return None