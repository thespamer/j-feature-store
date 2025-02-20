# FStore Architecture

## System Overview

```mermaid
graph TB
    subgraph Users
        DS[Data Scientist]
        ML[ML Engineer]
        DE[Data Engineer]
    end

    subgraph "Data Sources"
        DB[(Databases)]
        S3[(Data Lake)]
        ST[Streaming]
    end

    subgraph "FStore Platform"
        UI[Web UI]
        API[REST API]
        REG[Feature Registry]
        
        subgraph "Processing Layer"
            SPARK[Spark Processing]
            KAFKA[Kafka Streaming]
            VAL[Validation Engine]
        end
        
        subgraph "Storage Layer"
            REDIS[(Online Store<br/>Redis)]
            PG[(Offline Store<br/>PostgreSQL)]
            MONGO[(Metadata Store<br/>MongoDB)]
        end
        
        subgraph "Monitoring"
            MON[Monitoring Service]
            ALERT[Alert System]
            STATS[Statistics Engine]
        end
    end

    subgraph "Consumers"
        TRAIN[Training Pipeline]
        PRED[Prediction Service]
        DASH[Dashboards]
    end

    %% User Interactions
    DS --> UI
    ML --> UI
    DE --> UI
    UI --> API

    %% Data Input Flow
    DB --> SPARK
    S3 --> SPARK
    ST --> KAFKA

    %% Internal Processing
    API --> REG
    REG --> SPARK
    REG --> KAFKA
    SPARK --> VAL
    KAFKA --> VAL

    %% Storage
    VAL --> REDIS
    VAL --> PG
    REG --> MONGO

    %% Monitoring
    REDIS --> MON
    PG --> MON
    MON --> STATS
    STATS --> ALERT

    %% Output
    REDIS --> PRED
    PG --> TRAIN
    MON --> DASH
```

## Feature Lifecycle

```mermaid
sequenceDiagram
    participant U as User
    participant UI as Web UI
    participant API as REST API
    participant REG as Feature Registry
    participant PROC as Processing Layer
    participant STORE as Storage Layer
    participant MON as Monitoring

    U->>UI: Create Feature Definition
    UI->>API: POST /features
    API->>REG: Register Feature
    REG->>STORE: Store Metadata
    
    U->>UI: Upload/Connect Data
    UI->>API: POST /data
    API->>PROC: Process Data
    PROC->>STORE: Store Features
    
    loop Monitoring
        STORE->>MON: Send Metrics
        MON->>UI: Update Dashboard
    end
    
    U->>UI: Request Features
    UI->>API: GET /features
    API->>STORE: Fetch Features
    STORE->>UI: Return Features
```

## Data Flow Architecture

```mermaid
flowchart LR
    subgraph Input
        RDB[(Relational DB)]
        DOCS[(Documents)]
        STREAM((Stream Data))
    end

    subgraph Processing
        direction TB
        EXTRACT[Data Extraction]
        TRANS[Transformation]
        VALID[Validation]
        
        EXTRACT --> TRANS
        TRANS --> VALID
    end

    subgraph Storage
        ONLINE[(Online Store)]
        OFFLINE[(Offline Store)]
        META[(Metadata)]
    end

    subgraph Output
        TRAIN[Training]
        SERVE[Serving]
        ANALYZE[Analytics]
    end

    %% Input Connections
    RDB --> EXTRACT
    DOCS --> EXTRACT
    STREAM --> EXTRACT

    %% Processing to Storage
    VALID --> ONLINE
    VALID --> OFFLINE
    VALID --> META

    %% Storage to Output
    OFFLINE --> TRAIN
    ONLINE --> SERVE
    META --> ANALYZE
```

## Component Details

### 1. Input Layer
- Multiple data source support
- Batch and streaming ingestion
- Data validation and quality checks

### 2. Processing Layer
- Feature transformation pipeline
- Real-time processing
- Batch processing
- Point-in-time correct joins

### 3. Storage Layer
- Online store for low-latency serving
- Offline store for training data
- Metadata store for feature registry

### 4. Output Layer
- Feature serving API
- Training data export
- Analytics and monitoring

### 5. Monitoring Layer
- Data quality monitoring
- Feature drift detection
- Performance metrics
- Alerts and notifications
