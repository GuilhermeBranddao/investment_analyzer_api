Passo 1: Atualizar base de dados
- alembic revision --autogenerate -m "initial migration"
- alembic upgrade head


Passo 2: rodar etl
- task run_etl# Finalyzer


4. Construir a imagem Docker
Para construir sua imagem Docker, basta rodar o seguinte comando no diretório onde está o Dockerfile:

`docker build -t finalizer_api .`
5. Rodar o contêiner Docker
Após a construção da imagem, você pode rodar o contêiner com:

`docker run -p 5000:5000 finalizer_api`


# Rodar o container
$ docker start -a 9ceaee3de782

# Rodar o banco
$ docker start bfd41563828b

# Rodar ETL
docker exec -it 9ceaee3de782 poetry run task run_etl