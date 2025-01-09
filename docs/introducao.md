# Welcome to MkDocs

For full documentation visit [mkdocs.org](https://www.mkdocs.org).

## Commands

* `mkdocs new [dir-name]` - Create a new project.
* `mkdocs serve` - Start the live-reloading docs server.
* `mkdocs build` - Build the documentation site.
* `mkdocs -h` - Print help message and exit.

## Project layout

    mkdocs.yml    # The configuration file.
    docs/
        index.md  # The documentation homepage.
        ...       # Other markdown pages, images and other files..


```mermaid
graph TD
    A[Usuário acessa a plataforma] --> B[Cadastra-se com email e senha]
    B --> C[Confirma o cadastro]
    C --> D[Faz login]
    D --> E{Deseja criar uma carteira?}
    E -- Sim --> F[Cria uma nova carteira]
    E -- Não --> G[Explora a plataforma]
    F --> H[Adiciona ativos à carteira]
    H --> I[Visualiza relatórios e métricas]
    G --> I
```

# Fluxo do Usuário

```mermaid
graph TD
    A[Início] --> B[Cadastro]
    B --> C[Login]
    C --> D[Criação de Carteira]
    D --> E[Adição de Ativos]
    E --> F[Visualização de Relatórios]
    F --> G[Análise de Desempenho]
    G --> H[Fim]
```

### Como fica:
1. **A:** O usuário inicia no sistema.
2. **B:** Realiza o cadastro.
3. **C:** Faz login na plataforma.
4. **D:** Cria sua carteira de investimentos.
5. **E:** Adiciona ativos à carteira.
6. **F:** Visualiza relatórios e insights.
7. **G:** Analisa o desempenho da carteira.
8. **H:** Conclui a interação.

---

### Exemplo: Diagrama de Sequência para Cadastro de Usuário

```markdown
# Sequência de Cadastro
```
```mermaid
sequenceDiagram
    participant User as Usuário
    participant App as Aplicação
    participant DB as Banco de Dados

    User->>App: Preenche dados de cadastro
    App->>DB: Valida e salva dados
    DB-->>App: Confirmação de sucesso
    App-->>User: Retorna mensagem "Cadastro realizado com sucesso"
```

---

### Exemplo: Diagrama de Gantt para o Desenvolvimento do Projeto

```markdown
# Planejamento do Projeto
```
```mermaid
gantt
    title Planejamento do Projeto de Finanças
    dateFormat  YYYY-MM-DD
    section Cadastro de Usuário
    Design      :a1, 2025-01-01, 7d
    Implementação :after a1, 10d
    Testes      :after a1, 5d
    section Gestão de Carteira
    Design      :a2, 2025-01-15, 7d
    Implementação :after a2, 10d
    Testes      :after a2, 5d
    section Relatórios
    Design      :a3, 2025-02-01, 7d
    Implementação :after a3, 15d
    Testes      :after a3, 5d

```
---

### Exemplo: Diagrama de Gantt para o Desenvolvimento do Projeto

```markdown
# Planejamento do Projeto
```

```mermaid
gantt
    title Planejamento do Projeto de Finanças
    dateFormat  YYYY-MM-DD
    section Cadastro de Usuário
    Design      :a1, 2025-01-01, 7d
    Implementação :after a1, 10d
    Testes      :after a1, 5d
    section Gestão de Carteira
    Design      :a2, 2025-01-15, 7d
    Implementação :after a2, 10d
    Testes      :after a2, 5d
    section Relatórios
    Design      :a3, 2025-02-01, 7d
    Implementação :after a3, 15d
    Testes      :after a3, 5d
```

### Como fica:
- **Cadastro de Usuário:** Planejado para começar no início do projeto.
- **Gestão de Carteira:** Começa após o cadastro estar completo.
- **Relatórios:** Iniciado depois que a gestão de carteira for testada.

---

### Instruções de Uso
1. Certifique-se de que o **Mermaid** está habilitado no seu tema MkDocs.
2. Copie os blocos de código acima e insira-os nos arquivos `.md` dentro de sua documentação.
3. Visualize no navegador com `mkdocs serve`.

Se precisar de algo mais específico, posso ajudar!



---

## **Explicação do Fluxo**

- **A → B**: O usuário acessa a plataforma e se cadastra.
- **B → C**: Confirmação do cadastro via email ou outro método.
- **C → D**: O usuário faz login.
- **D → E**: O sistema pergunta se deseja criar uma carteira:
  - **Sim**: Ele pode criar e configurar uma nova carteira.
  - **Não**: Ele pode explorar outras áreas da plataforma.
- **F → H**: Dentro da carteira, o usuário adiciona ativos.
- **H → I**: O sistema apresenta relatórios sobre o desempenho da carteira.

---

### Outro Exemplo: Diagrama de Relação Entre Entidades

```markdown
# Estrutura da Base de Dados
```
```mermaid
erDiagram
    Usuario {
        int id PK
        string nome
        string email
        string senha
    }
    Carteira {
        int id PK
        string nome
        int usuario_id FK
    }
    Ativo {
        int id PK
        string nome
        float valor
        int carteira_id FK
    }

    Usuario ||--o{ Carteira : possui}
    Carteira ||--o{ Ativo : contém}
```