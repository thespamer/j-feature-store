# Guia de Conexão com Fontes de Dados - FStore

Este guia explica como conectar diferentes tipos de fontes de dados ao FStore para extração de features.

## Sumário
- [Bancos de Dados Relacionais](#bancos-de-dados-relacionais)
  - [PostgreSQL](#postgresql)
  - [MySQL](#mysql)
- [Data Lakes](#data-lakes)
  - [Amazon S3](#amazon-s3)
  - [Azure Data Lake](#azure-data-lake)
- [Streaming](#streaming)
  - [Apache Kafka](#apache-kafka)
  - [Apache Pulsar](#apache-pulsar)
- [API REST](#api-rest)
- [Exemplos Completos](#exemplos-completos)

## Bancos de Dados Relacionais

### PostgreSQL

O conector PostgreSQL permite extrair features de tabelas PostgreSQL usando consultas SQL.

```python
from fstore.connectors import PostgreSQLConnector

# Configuração da conexão
config = {
    "host": "localhost",
    "port": 5432,
    "database": "mydb",
    "user": "user",
    "password": "password"
}

# Inicializar conector
pg_connector = PostgreSQLConnector(config)

# Registrar feature usando SQL
feature_def = {
    "name": "customer_lifetime_value",
    "query": """
        SELECT 
            customer_id,
            SUM(order_value) as lifetime_value
        FROM orders
        GROUP BY customer_id
    """,
    "update_frequency": "1h"
}

pg_connector.register_feature(feature_def)
```

Recursos suportados:
- Consultas SQL complexas
- Agregações temporais
- Joins entre tabelas
- Atualização incremental
- Cache de resultados

### PostgreSQL com Query Customizada

Para criar uma feature usando uma query SQL específica do PostgreSQL, siga este exemplo:

```python
from fstore.connectors import PostgreSQLConnector
from fstore import FeatureStore

# 1. Configurar conexão com PostgreSQL
postgres_config = {
    "host": "localhost",  # ou seu host
    "port": 5432,        # sua porta
    "database": "mydb",  # seu database
    "user": "user",      # seu usuário
    "password": "pass"   # sua senha
}

# 2. Inicializar o Feature Store e o conector
store = FeatureStore()
pg_connector = PostgreSQLConnector(postgres_config)

# 3. Definir a feature com sua query customizada
feature_definition = {
    "name": "customer_purchase_frequency",
    "description": "Frequência de compras do cliente nos últimos 30 dias",
    "entity_id": "customer",
    "feature_group": "customer_metrics",
    "query": """
        WITH customer_purchases AS (
            SELECT 
                customer_id,
                COUNT(*) as purchase_count,
                COUNT(*) / 30.0 as purchase_frequency
            FROM orders
            WHERE created_at >= NOW() - INTERVAL '30 days'
            GROUP BY customer_id
        )
        SELECT 
            customer_id as entity_id,
            purchase_frequency as value,
            NOW() as timestamp
        FROM customer_purchases
    """,
    "schedule": "0 0 * * *"  # Executa diariamente à meia-noite
}

# 4. Registrar a feature
store.register_feature(
    feature_definition,
    connector=pg_connector
)
```

#### Requisitos da Query

A query SQL deve seguir estas regras:
1. Retornar exatamente 3 colunas:
   - `entity_id`: identificador da entidade
   - `value`: valor da feature
   - `timestamp`: momento da medição

2. Pode utilizar recursos SQL avançados:
   - Subconsultas
   - CTEs (WITH clauses)
   - Joins
   - Funções de agregação
   - Window functions

#### Agendamento

O campo `schedule` aceita expressões cron para definir a frequência de atualização:
- `0 0 * * *`: diário à meia-noite
- `0 */1 * * *`: a cada hora
- `0 0 * * 0`: semanal
- `0 0 1 * *`: mensal

#### Exemplo Completo

Um exemplo completo está disponível em `examples/custom_postgres_feature.py`.

### MySQL

Similar ao PostgreSQL, o conector MySQL permite extrair features de bancos MySQL.

```python
from fstore.connectors import MySQLConnector

mysql_config = {
    "host": "localhost",
    "port": 3306,
    "database": "mydb",
    "user": "user",
    "password": "password"
}

mysql_connector = MySQLConnector(mysql_config)
```

## Data Lakes

### Amazon S3

O conector S3 permite processar arquivos em diversos formatos (Parquet, CSV, JSON) armazenados no Amazon S3.

```python
from fstore.connectors import S3Connector

s3_config = {
    "bucket": "my-feature-store",
    "aws_access_key_id": "YOUR_ACCESS_KEY",
    "aws_secret_access_key": "YOUR_SECRET_KEY",
    "region": "us-east-1"
}

# Inicializar conector S3
s3_connector = S3Connector(s3_config)

# Registrar feature usando Parquet
feature_def = {
    "name": "user_behavior_features",
    "path": "features/user_behavior/*.parquet",
    "format": "parquet",
    "update_frequency": "1d"
}

s3_connector.register_feature(feature_def)
```

Formatos suportados:
- Apache Parquet
- CSV
- JSON
- Apache ORC

### Azure Data Lake

Para dados armazenados no Azure Data Lake Storage.

```python
from fstore.connectors import AzureDataLakeConnector

adls_config = {
    "account_name": "mystorageaccount",
    "container": "mycontainer",
    "credential": "YOUR_SAS_TOKEN"
}

adls_connector = AzureDataLakeConnector(adls_config)
```

## Streaming

### Apache Kafka

O conector Kafka permite processar features em tempo real a partir de tópicos Kafka.

```python
from fstore.connectors import KafkaConnector

kafka_config = {
    "bootstrap_servers": "localhost:9092",
    "group_id": "feature_store_group",
    "auto_offset_reset": "latest"
}

kafka_connector = KafkaConnector(kafka_config)

# Configurar processamento de streaming
feature_def = {
    "name": "user_current_session",
    "topic": "user_events",
    "value_field": "session_data",
    "window_size": "5m"
}

kafka_connector.register_streaming_feature(feature_def)
```

Recursos:
- Processamento em tempo real
- Janelas deslizantes
- Agregações em tempo real
- Tratamento de atrasos
- Checkpointing

### Apache Pulsar

Similar ao Kafka, mas usando Apache Pulsar como fonte de streaming.

```python
from fstore.connectors import PulsarConnector

pulsar_config = {
    "service_url": "pulsar://localhost:6650",
    "subscription_name": "feature_store_sub"
}

pulsar_connector = PulsarConnector(pulsar_config)
```

## API REST

### Envio de Eventos via API

Você pode enviar valores de features diretamente via API REST, ideal para:
- Aplicações que geram features em tempo real
- Integração com sistemas externos
- Testes e simulações
- POCs e protótipos rápidos

#### Exemplo Básico em Python

```python
import requests
from datetime import datetime

def send_feature_value(feature_id: str, entity_id: str, value: float):
    """
    Envia um valor de feature via API
    """
    url = "http://localhost:8000/api/v1/features/{}/values".format(feature_id)
    
    payload = {
        "entity_id": entity_id,
        "value": value,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    response = requests.post(url, json=payload)
    return response.status_code == 200

# Exemplo de uso
success = send_feature_value(
    feature_id="customer_purchase_amount",
    entity_id="customer_123",
    value=99.99
)
print(f"Envio {'bem-sucedido' if success else 'falhou'}")
```

#### Simulação de Múltiplos Eventos

Para casos onde você precisa simular ou enviar múltiplos eventos:

```python
import random
import time

def simulate_events():
    """
    Simula eventos de features para demonstração
    """
    feature_configs = [
        {
            "feature_id": "customer_purchase_amount",
            "entity_ids": ["customer_1", "customer_2"],
            "min_value": 10.0,
            "max_value": 1000.0
        },
        {
            "feature_id": "product_stock_level",
            "entity_ids": ["product_1", "product_2"],
            "min_value": 0.0,
            "max_value": 100.0
        }
    ]
    
    while True:
        for config in feature_configs:
            for entity_id in config["entity_ids"]:
                value = random.uniform(config["min_value"], config["max_value"])
                send_feature_value(config["feature_id"], entity_id, value)
        time.sleep(5)  # Espera 5 segundos entre lotes
```

#### Requisitos da API

1. **Endpoint**: 
```http
POST /api/v1/features/{feature_id}/values
```

2. **Payload**:
```json
{
    "entity_id": "string",    // ID da entidade (ex: customer_123)
    "value": 0.0,            // Valor numérico da feature
    "timestamp": "string"     // ISO format (ex: 2024-02-20T22:39:38Z)
}
```

3. **Respostas**:
- 200: Sucesso
- 404: Feature não encontrada
- 400: Payload inválido

#### Melhores Práticas

1. **Tratamento de Erros**:
```python
try:
    success = send_feature_value(feature_id, entity_id, value)
except requests.exceptions.RequestException as e:
    print(f"Erro na requisição: {str(e)}")
```

2. **Envio em Lote**:
```python
def send_batch_values(features: List[Dict]):
    url = "http://localhost:8000/api/v1/features/batch"
    response = requests.post(url, json=features)
    return response.status_code == 200
```

3. **Retry em Falhas**:
```python
from tenacity import retry, stop_after_attempt

@retry(stop=stop_after_attempt(3))
def send_feature_with_retry(feature_id, entity_id, value):
    return send_feature_value(feature_id, entity_id, value)
```

#### Exemplo Completo

Um exemplo completo de implementação está disponível em `examples/send_feature_events.py`.

## Exemplos Completos

Veja exemplos completos de implementação no diretório `examples/` do repositório:

- `examples/postgres_features.py`: Exemplo de extração de features do PostgreSQL
- `examples/kafka_streaming.py`: Processamento de features em tempo real com Kafka
- `examples/s3_batch_processing.py`: Processamento em batch de dados do S3

### Exemplo PostgreSQL
```python
# Importar do examples/postgres_features.py
from fstore import FeatureStore
from fstore.connectors import PostgresConnector

store = FeatureStore()
connector = PostgresConnector({
    "host": "localhost",
    "port": 5432,
    "database": "mydatabase",
    "user": "myuser",
    "password": "mypassword"
})

# Criar e atualizar feature
feature = store.create_feature(
    name="customer_total_purchases",
    query="SELECT customer_id, SUM(amount) FROM purchases GROUP BY customer_id"
)
store.update_feature_values(feature.name, connector)
```

### Exemplo Kafka Streaming
```python
# Importar do examples/kafka_streaming.py
from fstore import FeatureStore
from fstore.connectors import KafkaConnector

store = FeatureStore()
connector = KafkaConnector({
    "bootstrap_servers": "localhost:9092",
    "group_id": "feature_store_group"
})

# Configurar streaming
feature = store.create_feature(
    name="customer_last_action",
    stream_config={
        "topic": "customer_events",
        "value_field": "action"
    }
)
store.start_streaming_feature(feature.name, connector)
```

### Exemplo S3 Batch
```python
# Importar do examples/s3_batch_processing.py
from fstore import FeatureStore
from fstore.connectors import S3Connector

store = FeatureStore()
connector = S3Connector({
    "bucket": "my-feature-store",
    "aws_access_key_id": "YOUR_KEY",
    "aws_secret_access_key": "YOUR_SECRET"
})

# Configurar processamento em batch
feature = store.create_feature(
    name="customer_lifetime_value",
    batch_config={
        "path": "customer_transactions/*.parquet",
        "schedule": "0 0 * * *"  # Diariamente
    }
)
store.run_batch_processing(feature.name)
```

## Suporte

Para mais informações ou suporte:
1. Consulte a documentação completa em `/docs`
2. Veja os exemplos em `/examples`
3. Abra uma issue no GitHub
4. Entre em contato com a equipe de suporte
