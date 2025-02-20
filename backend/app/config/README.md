# Configuração de Data Sources

Este diretório contém as configurações dos data sources do Feature Store.

## Estrutura

- `settings.py`: Configurações gerais e carregamento de configurações
- `datasources.yaml`: Configurações específicas dos data sources

## Como Configurar

1. **Usando Variáveis de Ambiente**

Configure as variáveis de ambiente necessárias:

```bash
# PostgreSQL
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=fstore
export POSTGRES_USER=myuser
export POSTGRES_PASSWORD=mypassword

# Kafka
export KAFKA_SERVERS=localhost:9092
export KAFKA_GROUP=fstore_group

# AWS S3
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_REGION=us-east-1
export S3_BUCKET=my-feature-store
```

2. **Usando arquivo datasources.yaml**

Edite o arquivo `datasources.yaml` com suas configurações:

```yaml
postgres:
  host: localhost
  port: 5432
  database: fstore
  user: myuser
  password: mypassword

kafka:
  bootstrap_servers: localhost:9092
  group_id: fstore_group

s3:
  region_name: us-east-1
  bucket: my-feature-store
```

## Prioridade das Configurações

1. Variáveis de ambiente (maior prioridade)
2. Arquivo datasources.yaml
3. Configurações padrão em settings.py (menor prioridade)

## Exemplos de Uso

Veja exemplos completos de uso em:
- `/examples/postgres_features.py`
- `/examples/kafka_streaming.py`
- `/examples/s3_batch_processing.py`
