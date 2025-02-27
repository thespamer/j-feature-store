# JStore - Plataforma Moderna de Feature Store

JStore é uma plataforma poderosa e escalável de Feature Store que ajuda cientistas de dados e engenheiros de ML a gerenciar, armazenar e servir features para aplicações de machine learning.

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

### Como a JStore se Destaca

A JStore oferece uma solução moderna e completa para estes desafios:

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
- **Processamento**:
  - Apache Spark para processamento distribuído
  - Apache Kafka para streaming de eventos
- **Armazenamento**:
  - Store Online: Redis (cache e serving)
  - Store Offline: PostgreSQL (features processadas)
  - Store de Metadados: MongoDB (configurações)

## Componentes Principais

1. **Feature Processor**
   - Processamento distribuído com Spark
   - Consumo de eventos do Kafka
   - Transformações SQL
   - Persistência no PostgreSQL

2. **Feature Registry**
   - Gerenciamento de metadados
   - Versionamento de features
   - Configurações de transformação
   - Armazenamento no MongoDB

3. **Feature Serving**
   - Cache em Redis
   - API REST com FastAPI
   - Serving em tempo real
   - Monitoramento e logs

## Exemplo de Uso

```python
# Enviar evento para processamento
from kafka import KafkaProducer
import json

producer = KafkaProducer(bootstrap_servers='localhost:9092')

event = {
    "feature_group": "user_metrics",
    "data": [
        {
            "user_id": "user_123",
            "session_duration": 300,
            "page_views": 10
        }
    ],
    "transformation": """
        SELECT
            user_id,
            AVG(session_duration) as avg_session_duration,
            SUM(page_views) as total_page_views
        FROM input_data
        GROUP BY user_id
    """
}

producer.send('feature-events', json.dumps(event).encode())
```

## Configuração

1. **Dependências**
   ```bash
   pip install -r requirements.txt
   ```

2. **Variáveis de Ambiente**
   ```bash
   # Kafka
   KAFKA_BOOTSTRAP_SERVERS=localhost:9092
   
   # PostgreSQL
   POSTGRES_URI=postgresql://postgres:postgres@localhost:5432/fstore
   
   # Redis
   REDIS_URI=redis://localhost:6379
   
   # MongoDB
   MONGODB_URI=mongodb://localhost:27017/fstore
   ```

3. **Docker Compose**
   ```bash
   docker-compose up -d
   ```

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

### 1. Criando Features via Interface Web

1. Acesse a interface web em http://localhost:3000
2. Navegue até a página "Features"
3. Clique no botão "+" para criar uma nova feature
4. Preencha os campos básicos:
   - Nome da feature
   - Descrição
   - Tipo (numerical, categorical, temporal)
   - Entity ID

5. Para adicionar transformações:
   - Ative o switch "Enable SQL Transformation"
   - Insira a query SQL de transformação, exemplo:
     ```sql
     SELECT
       user_id,
       AVG(session_duration) as avg_session_duration,
       SUM(page_views) as total_page_views
     FROM input_data
     GROUP BY user_id
     ```
   - Selecione a janela de agregação (1h, 6h, 12h, 1d, 7d, 30d)

### 2. Criando Features via API

Você pode criar features programaticamente usando a API, seja localmente ou apontando para uma instância remota da feature store.

#### Exemplo Local
```python
import requests
import json

# Criar feature com transformação
feature_definition = {
    "name": "user_metrics",
    "description": "Métricas agregadas do usuário",
    "type": "numerical",
    "entity_id": "user_id",
    "transformation": {
        "sql_query": """
            SELECT
                user_id,
                AVG(session_duration) as avg_session_duration,
                SUM(page_views) as total_page_views
            FROM input_data
            GROUP BY user_id
        """,
        "aggregation_window": "1d"
    }
}

response = requests.post(
    "http://localhost:8000/api/v1/features/",
    json=feature_definition
)
print(response.json())
```

#### Exemplo Remoto
```python
from j_feature_store import FeatureStoreClient

# Inicializar cliente
client = FeatureStoreClient(
    host="feature-store.seu-dominio.com",  # Endereço da sua feature store
    port=443,                              # Porta (443 para HTTPS)
    use_ssl=True,                          # Usar HTTPS
    api_key="seu-api-key"                  # Chave de API para autenticação
)

# Criar feature com transformação
feature = client.create_feature(
    name="user_metrics",
    description="Métricas agregadas do usuário",
    type="numerical",
    entity_id="user_id",
    transformation={
        "sql_query": """
            SELECT
                user_id,
                AVG(session_duration) as avg_session_duration,
                SUM(page_views) as total_page_views
            FROM input_data
            GROUP BY user_id
        """,
        "aggregation_window": "1d"
    }
)

# Configurar conexão com Kafka para envio de eventos
client.configure_kafka(
    bootstrap_servers="kafka.seu-dominio.com:9092",
    security_protocol="SASL_SSL",
    sasl_mechanism="PLAIN",
    sasl_plain_username="seu-usuario",
    sasl_plain_password="sua-senha"
)

# Enviar eventos
client.send_events(
    topic="feature-events",
    events=[{
        "user_id": "user_123",
        "session_duration": 300,
        "page_views": 10,
        "timestamp": "2025-02-27T12:00:00Z"
    }]
)

# Consultar valores processados
values = client.get_feature_values(
    feature_name="user_metrics",
    entity_id="user_123",
    start_time="2025-02-26T00:00:00Z",
    end_time="2025-02-27T23:59:59Z"
)
print(values)
```

Este exemplo mostra como:
1. Conectar-se a uma feature store remota de forma segura
2. Criar features com transformações
3. Configurar conexão segura com Kafka
4. Enviar eventos e consultar valores

Para usar este exemplo, você precisará:
1. URL da sua feature store
2. Chave de API para autenticação
3. Credenciais do Kafka
4. Certificados SSL se necessário

### 3. Enviando Dados para Processamento

Após criar a feature, você pode enviar dados para processamento:

```python
# Enviar evento para processamento
from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers='localhost:9092')

event = {
    "user_id": "user_123",
    "session_duration": 300,
    "page_views": 10,
    "timestamp": "2025-02-27T12:00:00Z"
}

producer.send('feature-events', json.dumps(event).encode())
```

### 4. Consultando Valores de Features

Para consultar os valores processados:

```python
# Consultar valores da feature
response = requests.get(
    "http://localhost:8000/api/v1/features/user_metrics/values/user_123"
)
print(response.json())
```

## Monitoramento com Prometheus

O projeto utiliza Prometheus para monitoramento de métricas. Para acessar:

1. Inicie os serviços (se ainda não estiverem rodando):
```bash
docker-compose up -d
```

2. Acesse o Prometheus UI:
- URL: http://localhost:9090

### Métricas Disponíveis
- Feature Processor: http://localhost:9090/targets
  - Métricas de processamento de features
  - Performance do processamento
  - Status dos jobs

- Spark Metrics: http://localhost:9090/targets
  - Métricas do Spark
  - Utilização de recursos
  - Performance dos jobs

### Queries Úteis
- Total de features processadas:
```
rate(feature_processor_processed_total[5m])
```

- Tempo médio de processamento:
```
avg_over_time(feature_processor_processing_time_seconds[5m])
```

## Demo App

O projeto inclui uma aplicação de demonstração que ajuda a entender como a Feature Store funciona na prática. A demo está localizada no diretório `demo/` e inclui:

### Funcionalidades da Demo
- Geração automática de dados de exemplo
- Criação de um grupo de features "Customer Metrics"
- Features de demonstração:
  - `total_purchases`: Total de compras do cliente
  - `average_ticket`: Ticket médio do cliente

### Como Executar a Demo

```bash
# Navegue até o diretório demo
cd demo

# Execute o script de geração de dados
python generate_data.py
```

A demo é útil para:
- Entender como a feature store funciona
- Ter dados de exemplo para começar a usar o sistema
- Servir como referência para implementação de novas features

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

## Testes

### Executando os Testes

Os testes são executados em um container Docker isolado:

```bash
# Executar todos os testes
docker-compose run --rm backend-test

# Executar testes específicos
docker-compose run --rm backend-test pytest tests/test_features.py -v

# Executar testes com cobertura
docker-compose run --rm backend-test pytest --cov=app --cov-report=term-missing
```

### Desenvolvimento Local

1. Inicie os serviços de infraestrutura:
```bash
docker-compose up -d mongodb redis kafka postgres
```

2. Execute o backend em modo de desenvolvimento:
```bash
cd backend
pip install -r requirements.txt
pip install -r requirements.test.txt
uvicorn app.main:app --reload
```

3. Execute o frontend em modo de desenvolvimento:
```bash
cd frontend
npm install
npm start
```

## API Documentation

A documentação da API está disponível em:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/amazing-feature`)
3. Adicione testes para sua feature
4. Commit suas mudanças (`git commit -m 'Add amazing feature'`)
5. Push para a branch (`git push origin feature/amazing-feature`)
6. Abra um Pull Request

## License

MIT
