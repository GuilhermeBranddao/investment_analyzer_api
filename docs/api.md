# API (Se houver uma)

Inclua documentação para a API do projeto se ela existir, seguindo um formato como OpenAPI/Swagger:

Endpoints:

`POST /users/register`: Criar usuário.
`POST /auth/login`: Login.
`GET /portfolio`: Listar carteiras.
`POST /portfolio`: Criar carteira.
Exemplo de requisição:

POST /portfolio
```python
{
  "name": "Minha Carteira",
  "description": "Carteira para ações de longo prazo."
}
```

Exemplo de resposta:
```python
{
  "id": 1,
  "name": "Minha Carteira",
  "created_at": "2025-01-06T12:34:56"
}

```
