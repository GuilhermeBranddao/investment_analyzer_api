- Tabela **user**
    - id: int
    - name: str
    - email: str
    - password: str
    - role_id: int
    - is_active: bool
    - created_at: datetime
    - updated_at: datetime

- Tabela **status**
    - id: int
    - name: str

- Tabela **assets** (Lista de ativos)
    - id: int
    - symbol: str = "IRDM11"
    - name: str = "Fundo Investimento Imobiliario Iridium Rec"
    - category: str = "FII"
    - market_id: int = 1

- Tabela **market** (Tipo do mercado da ação, para especificar se é uma ação, FII, etc.)
    - id: int
    - name: str
    - description: str
    - country_id: int

- Tabela **country**
    - id: int
    - name: str
    - iso_code: str

- Tabela **asset_price_history** (Lista de transações - Ativos que as pessoas adicionam)
    - id: int
    - date: datetime
    - open: float
    - high: float
    - low: float
    - close: float
    - adjusted_close: float
    - volume: int
    - dividends: float
    - stock_splits: float
    - asset_id: int


- Tabela **user_asset_transactions**
    - id: int
    - quantity: int
    - unit_value: float
    - purchase_value: float
    - date: datetime 
    - transaction_type_id: str
    - asset_id
    - created_at: datetime
    - updated_at: datetime

- Tabela **transaction_types**
    - id: int
    - type_name: str

- Tabela **portfolio**
    - id: int
    - name: str
    - user_id: int
    - description: str
    - created_at: datetime
    - updated_at: datetime

Tabela **portfolio_assets**
    - id: int
    - portfolio_id: int (relacionando com a tabela `portfolio`)
    - asset_id: int (relacionando com a tabela `ticker`)
    - quantity: int (quantidade de ativos no portfólio)
    - created_at: datetime
    - updated_at: datetime

- Relacionamentos
- Um usuario pode uma ou varias **Carteitas**
    - Guilherme tem as carteiras 'carteira apo', 'carteira abc', 'carteira mji'

- Apartir de uma **cartrira** o usuairo pode adicionar um ou varios ativos a essa carteira
    - Guilherme a carteira 'carteira abc' e tem os ativos 'ITSA4', 'SAPR4', 'CPLE6', 'BBAS3' atrelados a ela


Para cada ativo adicionado em **atividades_historicas** 

A tabela **eventos** é responsavel por fazer a identificação se a ativadade historica é de compra, venda ou outra 

Em **ativos_historicos** vou sauvar todos os dados historicos de um determinado ativo


Adição: status: str ou role: str (opcional, caso você tenha diferentes tipos de usuários, como "admin", "regular", etc.).