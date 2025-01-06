import re
from fastapi import HTTPException, status

def validate_name(name: str):
    """
    Valida o nome do usuário.
    Regras:
    - Deve ter entre 3 e 50 caracteres.
    - Não pode conter números ou caracteres especiais.
    - Deve conter apenas letras e espaços.
    """
    if not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O nome não pode estar vazio."
        )
    if len(name.replace(" ", "")) < 3 or len(name) > 50:
        raise HTTPException(    
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O nome deve ter entre 3 e 50 caracteres."
        )
    if not re.match(r"^[a-zA-ZÀ-ÿ\s]+$", name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O nome deve conter apenas letras e espaços."
        )
    return True
