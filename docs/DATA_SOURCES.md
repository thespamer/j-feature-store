# Guia de Conexão com Fontes de Dados - FStore

Este guia explica como conectar diferentes tipos de fontes de dados ao FStore para extração de features.

## Sumário
- [Bancos de Dados Relacionais](#bancos-de-dados-relacionais)
- [Data Lakes](#data-lakes)
- [Streaming](#streaming)
- [Outras Fontes](#outras-fontes)

## Bancos de Dados Relacionais

### PostgreSQL

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

### MySQL

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

### Azure Data Lake

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

```python
from fstore.connectors import KafkaConnector

kafka_config = {
    "bootstrap_servers": "localhost:9092",
    "group_id": "feature_store_group",
    "auto_offset_reset": "latest"
}

# Inicializar conector Kafka
kafka_connector = KafkaConnector(kafka_config)

# Registrar feature de streaming
streaming_feature = {
    "name": "user_click_stream",
    "topic": "user_clicks",
    "window_size": "5m",
    "aggregations": [
        {"type": "count", "field": "click_id"},
        {"type": "sum", "field": "duration"}
    ]
}

kafka_connector.register_streaming_feature(streaming_feature)
```

### Apache Flink

```python
from fstore.connectors import FlinkConnector

flink_config = {
    "job_manager_url": "localhost:8081",
    "parallelism": 4
}

flink_connector = FlinkConnector(flink_config)
```

## Outras Fontes

### REST APIs

```python
from fstore.connectors import RESTConnector

api_config = {
    "base_url": "https://api.example.com/v1",
    "auth_token": "YOUR_API_TOKEN",
    "rate_limit": 100  # requests per minute
}

# Inicializar conector REST
rest_connector = RESTConnector(api_config)

# Registrar feature usando API
feature_def = {
    "name": "weather_features",
    "endpoint": "/weather",
    "method": "GET",
    "params": {
        "location": "city_id",
        "metrics": ["temperature", "humidity", "pressure"]
    },
    "update_frequency": "1h"
}

rest_connector.register_feature(feature_def)
```

### MongoDB

```python
from fstore.connectors import MongoDBConnector

mongodb_config = {
    "host": "localhost",
    "port": 27017,
    "database": "features_db",
    "collection": "features"
}

mongodb_connector = MongoDBConnector(mongodb_config)
```

## Boas Práticas

1. **Segurança**
   - Nunca armazene credenciais no código
   - Use variáveis de ambiente ou gerenciadores de segredos
   - Implemente rotação de chaves quando possível

2. **Performance**
   - Configure índices apropriados
   - Use particionamento quando necessário
   - Implemente cache para queries frequentes

3. **Monitoramento**
   - Configure alertas para falhas de conexão
   - Monitore latência de queries
   - Acompanhe uso de recursos

4. **Manutenção**
   - Mantenha documentação atualizada
   - Faça backup regular dos dados
   - Implemente versionamento de schemas

## Troubleshooting

### Problemas Comuns

1. **Conexão Recusada**
   - Verifique firewall
   - Confirme credenciais
   - Verifique status do servidor

2. **Performance Baixa**
   - Analise plano de execução
   - Verifique índices
   - Otimize queries

3. **Dados Inconsistentes**
   - Verifique transformações
   - Confirme schema
   - Valide pipeline de dados

## Exemplos Completos

Veja exemplos completos de implementação no diretório `examples/` do repositório:
- `examples/postgres_features.py`
- `examples/kafka_streaming.py`
- `examples/s3_batch_processing.py`

## Suporte

Para mais informações ou suporte:
- Documentação: `docs/`
- Issues: GitHub Issues
- Comunidade: Slack Channel
