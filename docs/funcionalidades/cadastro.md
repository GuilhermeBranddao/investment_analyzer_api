# Cadastro de Usuários

## Como se cadastrar e fazer login.

### **1. Cadastro de Usuário**
- **POST** `/users/register`
  - Descrição: Cria um novo usuário.
  - Requisição:
    ```json
    {
      "username": "exemplo",
      "password": "senha123",
      "email": "email@exemplo.com"
    }
    ```
  - Resposta:
    ```json
    {
      "id": 1,
      "username": "exemplo",
      "email": "email@exemplo.com",
      "created_at": "2025-01-06T10:00:00"
    }
    ```



## Segurança de dados (exemplo: autenticação JWT).
