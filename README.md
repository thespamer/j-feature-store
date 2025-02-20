# FStore - Plataforma Moderna de Feature Store

FStore é uma plataforma poderosa e escalável de Feature Store que ajuda cientistas de dados e engenheiros de ML a gerenciar, armazenar e servir features para aplicações de machine learning.

## O que é uma Feature Store?

Uma Feature Store é um componente central da infraestrutura de Machine Learning que atua como um repositório centralizado para armazenar, gerenciar e servir features (características ou atributos) usadas em modelos de machine learning. Ela resolve vários desafios críticos no desenvolvimento e implantação de sistemas de ML:

### Principais Benefícios

1. **Consistência de Features**
   - Garante que as mesmas transformações sejam aplicadas tanto no treinamento quanto na inferência
   - Evita o "feature drift" entre ambientes de desenvolvimento e produção
   - Mantém a consistência entre diferentes modelos que usam as mesmas features

2. **Reutilização e Colaboração**
   - Permite que equipes compartilhem e reutilizem features
   - Reduz duplicação de esforços na engenharia de features
   - Facilita a colaboração entre cientistas de dados

3. **Governança e Rastreabilidade**
   - Mantém histórico de versões das features
   - Documenta transformações e linhagem de dados
   - Facilita auditorias e compliance

### Casos de Uso

1. **E-commerce - Recomendação de Produtos**
   ```python
   # Features do usuário
   user_features = {
       "avg_order_value": 150.0,
       "favorite_categories": ["electronics", "books"],
       "last_purchase_date": "2025-02-15"
   }
   ```

2. **Detecção de Fraude - Transações Financeiras**
   ```python
   # Features de transação
   transaction_features = {
       "amount": 1000.0,
       "merchant_category": "online_retail",
       "user_transaction_frequency": "high",
       "device_risk_score": 0.2
   }
   ```

3. **Marketing Personalizado - Segmentação de Clientes**
   ```python
   # Features de comportamento
   customer_features = {
       "engagement_score": 8.5,
       "email_open_rate": 0.75,
       "preferred_channel": "email",
       "lifetime_value": 2500.0
   }
   ```

### Como a FStore se Destaca

A FStore oferece uma solução moderna e completa para estes desafios:

1. **Processamento Dual-Store**
   - Store Online (Redis) para serving em tempo real
   - Store Offline (PostgreSQL) para treinamento em batch

2. **Transformações em Tempo Real**
   - Processamento de streams com Apache Kafka
   - Computação distribuída com Apache Spark

3. **API Flexível**
   - Interface REST para integração com qualquer stack
   - SDKs para Python e outras linguagens

4. **Monitoramento Avançado**
   - Métricas de qualidade de features
   - Alertas de drift e anomalias
   - Dashboards de performance

## Principais Funcionalidades

- Pipeline de Engenharia de Features
- Armazenamento Online/Offline de Features
- Registro e Versionamento de Features
- Serving de Features em Tempo Real
- Exportação em Lote de Features
- Monitoramento e Validação de Features
- Interface Web para Gerenciamento
- API REST para Integração
- Suporte para Múltiplas Fontes de Dados

## Arquitetura

- **Frontend**: React + TypeScript + Material-UI
- **Backend**: FastAPI (Python)
- **Processamento de Features**: Apache Spark
- **Armazenamento**:
  - Store Online: Redis
  - Store Offline: PostgreSQL
  - Store de Metadados: MongoDB
- **Fila de Mensagens**: Apache Kafka
- **Containerização**: Docker + Docker Compose

## Início Rápido

### 1. Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/fstore.git
cd fstore

# Instale as dependências
docker-compose up -d
```

### 2. Acessando a Interface

- Interface Web: http://localhost:3000
- Documentação da API: http://localhost:8000/docs

## Guia de Uso

### 1. Criando Features

#### Via Interface Web

1. Acesse http://localhost:3000
2. Navegue até "Features" > "Nova Feature"
3. Preencha os campos:
   - Nome da Feature
   - Descrição
   - Tipo (Numérico, Categórico, Temporal)
   - Entidade (ex: usuario, produto)
   - Tags
   - Fonte de Dados

#### Via API

```python
import requests

feature = {
    "name": "usuario_idade",
    "description": "Idade do usuário",
    "feature_type": "NUMERIC",
    "value_type": "INT",
    "entity": "usuario",
    "tags": ["demografia", "basico"],
}

response = requests.post(
    "http://localhost:8000/api/features/",
    json=feature
)
```

### 2. Ingestão de Dados

#### Batch (Arquivos)

1. Formatos suportados:
   - CSV
   - Parquet
   - JSON
   - SQL Databases

```python
# Exemplo de ingestão via Python
import pandas as pd
from fstore.client import FStoreClient

client = FStoreClient("http://localhost:8000")

# Carregar dados
df = pd.read_csv("dados_usuarios.csv")

# Registrar features
client.ingest_batch(
    entity="usuario",
    feature_group="demografia",
    dataframe=df
)
```

#### Streaming (Tempo Real)

```python
# Exemplo com Kafka
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Enviar dados
producer.send('feature_topic', {
    'entity_key': 'user_123',
    'feature_name': 'usuario_idade',
    'value': 25,
    'timestamp': '2025-02-20T15:45:11Z'
})
```

### 3. Transformação de Features

#### SQL

```sql
-- Exemplo de transformação SQL
SELECT 
    user_id,
    AVG(transaction_amount) as avg_transaction_value,
    COUNT(*) as transaction_count
FROM transactions
GROUP BY user_id
```

#### Python

```python
# Exemplo de transformação Python
def calculate_features(df):
    return df.groupby('user_id').agg({
        'transaction_amount': ['mean', 'count', 'sum']
    }).reset_index()
```

### 4. Recuperando Features

#### Para Treino (Offline)

```python
# Recuperar features para treino
features = client.get_training_features(
    entity="usuario",
    feature_list=["idade", "renda", "cidade"],
    start_date="2025-01-01",
    end_date="2025-02-20"
)
```

#### Para Inferência (Online)

```python
# Recuperar features em tempo real
features = client.get_online_features(
    entity="usuario",
    entity_keys=["user_123", "user_456"],
    feature_list=["idade", "renda", "cidade"]
)
```

### 5. Monitoramento

1. Métricas disponíveis:
   - Qualidade dos dados
   - Latência
   - Feature drift
   - Cobertura

2. Acessando métricas:
   - Dashboard: http://localhost:3000/monitoring
   - API: http://localhost:8000/api/monitoring/

### 6. Boas Práticas

1. **Nomenclatura de Features**:
   - Use snake_case
   - Prefixe com a entidade: `usuario_idade`
   - Seja descritivo: `produto_ultima_compra_dias`

2. **Documentação**:
   - Descreva cada feature
   - Adicione tags relevantes
   - Mantenha metadados atualizados

3. **Versionamento**:
   - Versione transformações
   - Documente mudanças
   - Mantenha compatibilidade

## Configuração de Desenvolvimento

### Pré-requisitos

- Docker & Docker Compose
- Python 3.9+
- Node.js 16+
- Java 11+ (para Spark)

### Desenvolvimento Local

1. Backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # ou `venv\Scripts\activate` no Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

2. Frontend:
```bash
cd frontend
npm install
npm start
```

## Troubleshooting

### Problemas Comuns

1. **Erro de Conexão com Redis**:
   ```bash
   docker-compose restart redis
   ```

2. **Kafka não Disponível**:
   ```bash
   docker-compose restart kafka zookeeper
   ```

3. **Limpeza Completa**:
   ```bash
   docker-compose down -v
   docker-compose up -d
   ```

## Licença

Licença MIT
