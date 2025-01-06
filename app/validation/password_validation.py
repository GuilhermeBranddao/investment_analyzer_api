import re
from fastapi import HTTPException, status

def validate_password(user_password: str, username: str):
    """
    Valida a senha do usuário com base em critérios de complexidade e segurança.

    Args:
        user_password (str): A senha fornecida pelo usuário.
        username (str): O nome de usuário para evitar senhas baseadas no nome de usuário.

    Raises:
        HTTPException: Se a senha não atender aos requisitos de segurança.
    """
    # 1. Senha deve ter pelo menos 8 caracteres
    if len(user_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A senha deve ter pelo menos 8 caracteres.",
        )

    # 2. A senha não deve conter o nome de usuário
    if username.lower() in user_password.lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A senha não pode conter o nome de usuário.",
        )

    # 3. Senha deve ter pelo menos uma letra maiúscula, uma letra minúscula e um número
    if not re.search(r'[A-Z]', user_password):  # Verificar letra maiúscula
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A senha deve conter pelo menos uma letra maiúscula.",
        )
    if not re.search(r'[a-z]', user_password):  # Verificar letra minúscula
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A senha deve conter pelo menos uma letra minúscula.",
        )
    if not re.search(r'[0-9]', user_password):  # Verificar número
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A senha deve conter pelo menos um número.",
        )

    # 4. Senha deve conter pelo menos um caractere especial [!@#$%*]
    if not any(char in user_password for char in "!@#$%*"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A senha deve conter pelo menos um caractere especial [!@#$%*].",
        )

    # 5. Verificar se a senha é uma senha fraca
    weak_passwords = [
        "123456", "password", "qwerty", "abc123", "letmein", "welcome", "password1"
    ]
    if user_password.lower() in weak_passwords:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Essa senha é muito fraca. Tente uma combinação mais forte.",
        )

    # 6. Senha não pode ter espaços em branco
    if " " in user_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A senha não pode conter espaços em branco.",
        )

    # 7. Senha não pode ser a mesma em um histórico recente
    # (Pode implementar um histórico de senhas ou verificar em uma lista)
    # Exemplo de verificação em uma lista de senhas anteriores
    previous_passwords = ["oldpassword1", "oldpassword2"]  # Exemplo de lista de senhas anteriores
    if user_password in previous_passwords:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você não pode reutilizar senhas antigas.",
        )

    # Se passar em todas as verificações, a senha é válida
    return True
