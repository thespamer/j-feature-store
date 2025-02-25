# Arquitetura da Feature Store

## Visão Geral

A Feature Store é uma plataforma moderna e escalável que suporta transformação, armazenamento e servimento de features para machine learning. A arquitetura é construída em torno dos princípios de confiabilidade, escalabilidade e facilidade de uso.

## Componentes

### 1. Serviço Backend
- **Tecnologia**: Python FastAPI
- **Propósito**: Fornece API REST para gerenciamento de features
- **Funcionalidades Principais**:
  - Operações CRUD de Features e Grupos de Features
  - Armazenamento e recuperação de valores de features
  - Integração com camada de cache
  - Tratamento de erros e validação

### 2. Processador de Features
- **Tecnologia**: Apache Spark
- **Propósito**: Processa atualizações de features em streaming
- **Funcionalidades Principais**:
  - Consumidor Kafka para atualizações em tempo real
  - Capacidades de processamento em batch
  - Validação e transformação de dados
  - Operações eficientes de escrita no PostgreSQL

### 3. Camada de Armazenamento

#### MongoDB
- Armazena metadados de features e grupos de features
- Otimizado para schema flexível e consultas em documentos
- Usado para descoberta e gerenciamento de features

#### PostgreSQL
- Armazena valores de features com schema rígido
- Otimizado para dados de séries temporais e agregações
- Suporta constraints de chave estrangeira e consultas complexas

#### Redis
- Faz cache de valores de features frequentemente acessados
- Reduz latência para servimento de features em tempo real
- Implementa invalidação de cache baseada em TTL

### 4. Fila de Mensagens
- **Tecnologia**: Apache Kafka
- **Propósito**: Gerencia atualizações de features em tempo real
- **Funcionalidades**:
  - Garante entrega confiável de mensagens
  - Suporta múltiplos consumidores
  - Mantém ordenação de mensagens

## Diagramas

### Diagrama de Classes

```mermaid
classDiagram
    class Feature {
        +str id
        +str name
        +str description
        +str type
        +dict metadata
        +datetime created_at
        +datetime updated_at
        +validate()
        +to_dict()
    }

    class FeatureGroup {
        +str id
        +str name
        +str description
        +List[str] feature_ids
        +dict metadata
        +datetime created_at
        +add_feature()
        +remove_feature()
        +get_features()
    }

    class Transformer {
        +str id
        +str type
        +dict params
        +dict state
        +fit(data)
        +transform(data)
        +save_state()
        +load_state()
    }

    class FeatureStore {
        +MongoClient metadata_store
        +Redis online_store
        +PostgresClient offline_store
        +register_feature()
        +get_feature()
        +update_feature()
        +delete_feature()
        +get_feature_value()
    }

    class FeatureProcessor {
        +KafkaConsumer consumer
        +SparkSession spark
        +process_event()
        +update_feature_values()
        +compute_statistics()
    }

    FeatureStore "1" -- "*" Feature
    FeatureStore "1" -- "*" FeatureGroup
    FeatureStore "1" -- "*" Transformer
    FeatureGroup "*" -- "*" Feature
    Feature "1" -- "0..1" Transformer
```

### Diagrama de Componentes

```mermaid
C4Component
    title Diagrama de Componentes da Feature Store

    Container_Boundary(api, "Camada API") {
        Component(rest_api, "API REST", "FastAPI", "Endpoints RESTful para gerenciamento")
        Component(auth, "Serviço Auth", "JWT", "Autenticação e autorização")
    }

    Container_Boundary(processing, "Camada de Processamento") {
        Component(feature_processor, "Processador de Features", "Python", "Processamento de features")
        Component(spark_jobs, "Jobs Spark", "PySpark", "Transformações em batch")
    }

    Container_Boundary(storage, "Camada de Armazenamento") {
        Component(metadata_store, "Metadata Store", "MongoDB", "Armazenamento de metadados")
        Component(online_store, "Online Store", "Redis", "Cache e servimento rápido")
        Component(offline_store, "Offline Store", "PostgreSQL", "Armazenamento persistente")
    }

    Container_Boundary(streaming, "Camada de Streaming") {
        Component(kafka, "Stream de Eventos", "Kafka", "Stream de eventos")
        Component(consumer, "Consumidor", "Python", "Consumo de eventos")
    }

    Container_Boundary(monitoring, "Camada de Monitoramento") {
        Component(health, "Health Check", "FastAPI", "Monitoramento de saúde")
        Component(metrics, "Métricas", "FastAPI", "Métricas do sistema")
    }

    Rel(rest_api, auth, "Usa")
    Rel(rest_api, metadata_store, "CRUD")
    Rel(rest_api, online_store, "Leitura/Escrita")
    Rel(feature_processor, kafka, "Consome")
    Rel(feature_processor, offline_store, "Persiste")
    Rel(feature_processor, online_store, "Atualiza")
    Rel(spark_jobs, offline_store, "Processa")
    Rel(consumer, kafka, "Consome")
    Rel(consumer, feature_processor, "Processa")
    Rel(health, metadata_store, "Verifica")
    Rel(health, online_store, "Verifica")
    Rel(health, offline_store, "Verifica")
    Rel(metrics, metadata_store, "Coleta")
```

### Fluxo de Dados

#### 1. Criação e Registro de Features
```mermaid
sequenceDiagram
    Cliente->>API: Requisição de Criação de Feature
    API->>Registro: Registra Feature
    Registro->>MongoDB: Armazena Metadados
    Registro->>Redis: Cache de Metadados
    API-->>Cliente: Resposta de Feature Criada
```

#### 2. Transformação e Armazenamento
```mermaid
sequenceDiagram
    Cliente->>API: Requisição para Armazenar Valor
    API->>Transformador: Transforma Valor
    Transformador->>MongoDB: Armazena Original & Transformado
    Transformador->>Redis: Cache do Último Valor
    API-->>Cliente: Resposta de Valor Armazenado
```

#### 3. Recuperação de Valores
```mermaid
sequenceDiagram
    Cliente->>API: Requisição de Valor
    API->>Redis: Verifica Cache
    alt Cache Hit
        Redis-->>API: Retorna Valor em Cache
    else Cache Miss
        API->>MongoDB: Consulta Valor
        API->>Transformador: Transforma se necessário
        API->>Redis: Atualiza Cache
        API-->>Cliente: Resposta com Valor
    end
```

#### 4. Gerenciamento de Versões
```mermaid
sequenceDiagram
    Cliente->>Registro: Registra Nova Versão
    Registro->>MongoDB: Armazena Config da Versão
    Registro->>Transformador: Atualiza Transformador
    Transformador->>Redis: Cache do Novo Transformador
    Registro-->>Cliente: Versão Registrada
```

## Fluxo de Dados

1. **Criação de Feature**:
   ```
   Cliente -> Backend -> MongoDB & PostgreSQL
   ```

2. **Atualizações de Valores de Features**:
   ```
   Cliente -> Backend -> Kafka -> Processador de Features -> PostgreSQL
   ```

3. **Recuperação de Valores de Features**:
   ```
   Cliente -> Backend -> Redis (Cache Hit) -> Resposta
                    -> PostgreSQL (Cache Miss) -> Redis -> Resposta
   ```

## Design do Schema

### Coleções MongoDB

#### Features
```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "feature_group_id": "string",
  "type": "string",
  "entity_id": "string",
  "tags": ["string"],
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

#### Grupos de Features
```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "entity_id": "string",
  "entity_type": "string",
  "tags": ["string"],
  "frequency": "string",
  "created_at": "datetime",
  "updated_at": "datetime",
  "features": ["string"]
}
```

### Tabelas PostgreSQL

#### features
```sql
CREATE TABLE features (
  id VARCHAR(255) PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### feature_values
```sql
CREATE TABLE feature_values (
  id SERIAL PRIMARY KEY,
  feature_id VARCHAR(255) REFERENCES features(id),
  entity_id VARCHAR(255) NOT NULL,
  value DOUBLE PRECISION NOT NULL,
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(feature_id, entity_id)
);
```

## Otimizações de Performance

1. **Estratégia de Cache**:
   - Redis faz cache de valores de features com TTL de 1 hora
   - Cache é atualizado no momento da escrita (write-through)
   - Suporta operações de leitura de alta vazão

2. **Indexação de Banco de Dados**:
   - Índices PostgreSQL em feature_id, entity_id e timestamp
   - Índices MongoDB em feature_group_id e entity_id
   - Otimizado para padrões comuns de consulta

3. **Processamento em Batch**:
   - Processador de Features usa Spark para atualizações em batch eficientes
   - Tamanhos de batch e janelas de processamento configuráveis
   - Otimização adaptativa de consultas

## Considerações de Segurança

1. **Acesso a Dados**:
   - Autenticação e autorização na API
   - Segurança na conexão com banco de dados
   - Rate limiting nos endpoints da API

2. **Validação de Dados**:
   - Validação de entrada em todos os endpoints da API
   - Verificação de tipos e constraints
   - Tratamento de erros e logging

## Monitoramento

1. **Métricas**:
   - Latência e vazão de requisições
   - Taxas de hit/miss do cache
   - Métricas de performance do banco de dados
   - Lag do consumidor Kafka

2. **Verificações de Saúde**:
   - Monitoramento de disponibilidade dos serviços
   - Status da conexão com banco de dados
   - Status da conexão com Kafka
   - Status da conexão com Redis
