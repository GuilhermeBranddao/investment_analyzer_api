import re
from fastapi import HTTPException, status

def validate_email(user_email: str, repository_user):
    """
    Valida o e-mail do usuário.

    Args:
        user_email (str): O e-mail fornecido pelo usuário.
        repository_user: O repositório de usuários para consulta no banco de dados.

    Raises:
        HTTPException: Se o e-mail não for válido ou já estiver em uso.
    """
    # 1. Verificar se o e-mail tem um formato válido
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    if not re.match(email_regex, user_email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de e-mail inválido.",
        )

    # 2. Verificar se já existe um usuário com este e-mail
    if repository_user.get_user_per_email(user_email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um usuário registrado com este e-mail.",
        )
    
    # Se passar nas verificações, o e-mail é válido
    return True
