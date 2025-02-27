# Arquitetura do J Feature Store

## Visão Geral
O J Feature Store é uma plataforma moderna para gerenciamento de features em projetos de Machine Learning, oferecendo uma solução completa para armazenamento, versionamento e servimento de features.

## Diagramas

### Diagrama de Componentes
```mermaid
graph TB
    subgraph Frontend
        UI[Interface do Usuário]
        API_Client[API Client]
    end
    
    subgraph Backend
        API[API REST]
        FeatureService[Feature Service]
        TransformationService[Transformation Service]
        ValidationService[Validation Service]
    end
    
    subgraph Storage
        MongoDB[(MongoDB)]
        Redis[(Redis Cache)]
        S3[(Object Storage)]
    end
    
    UI --> API_Client
    API_Client --> API
    API --> FeatureService
    API --> TransformationService
    API --> ValidationService
    FeatureService --> MongoDB
    FeatureService --> Redis
    TransformationService --> S3
```

### Diagrama de Infraestrutura
```mermaid
graph TB
    subgraph "Docker Network: j-feature-store-network"
        subgraph "Frontend Container (j-feature-store-frontend)"
            React[React App]
            style React fill:#e1f5fe
        end

        subgraph "Backend Container (j-feature-store-backend)"
            FastAPI[FastAPI]
            Uvicorn[Uvicorn Server]
            style FastAPI fill:#e8f5e9
            style Uvicorn fill:#e8f5e9
        end

        subgraph "MongoDB Container (j-feature-store-mongodb)"
            MongoDB[(MongoDB)]
            style MongoDB fill:#fff3e0
        end

        subgraph "Redis Container (j-feature-store-redis)"
            Redis[(Redis)]
            style Redis fill:#fce4ec
        end

        subgraph "MinIO Container (j-feature-store-minio)"
            MinIO[MinIO S3]
            style MinIO fill:#f3e5f5
        end
    end

    Browser[Browser] --> |"Port 3000"| React
    React --> |"Port 8000"| FastAPI
    FastAPI --> Uvicorn
    Uvicorn --> |"Port 27017"| MongoDB
    Uvicorn --> |"Port 6379"| Redis
    Uvicorn --> |"Port 9000"| MinIO

    classDef container fill:#f5f5f5,stroke:#333,stroke-width:2px;
    class React,FastAPI,Uvicorn,MongoDB,Redis,MinIO container;
```

### Detalhes dos Containers

#### Frontend Container
- **Nome**: j-feature-store-frontend
- **Porta**: 3000
- **Imagem**: node:18-alpine
- **Dependências**: Nenhuma
- **Volumes**: ./frontend:/app

#### Backend Container
- **Nome**: j-feature-store-backend
- **Porta**: 8000
- **Imagem**: python:3.11-slim
- **Dependências**: MongoDB, Redis, MinIO
- **Volumes**: ./backend:/app

#### MongoDB Container
- **Nome**: j-feature-store-mongodb
- **Porta**: 27017
- **Imagem**: mongo:6
- **Volumes**: mongodb_data:/data/db

#### Redis Container
- **Nome**: j-feature-store-redis
- **Porta**: 6379
- **Imagem**: redis:7-alpine
- **Volumes**: redis_data:/data

#### MinIO Container
- **Nome**: j-feature-store-minio
- **Portas**: 9000 (API), 9001 (Console)
- **Imagem**: minio/minio
- **Volumes**: minio_data:/data

### Rede Docker
- **Nome**: j-feature-store-network
- **Driver**: bridge
- **Subnet**: 172.20.0.0/16

### Volumes
- **mongodb_data**: Persistência do MongoDB
- **redis_data**: Persistência do Redis
- **minio_data**: Persistência do MinIO

## Comunicação entre Containers

1. **Frontend → Backend**
   - Protocol: HTTP/HTTPS
   - Porta: 8000
   - Endpoint Base: /api/v1

2. **Backend → MongoDB**
   - Protocol: MongoDB Wire Protocol
   - Porta: 27017
   - Connection String: mongodb://j-feature-store-mongodb:27017

3. **Backend → Redis**
   - Protocol: Redis Protocol
   - Porta: 6379
   - Connection String: redis://j-feature-store-redis:6379

4. **Backend → MinIO**
   - Protocol: HTTP/HTTPS
   - Porta: 9000
   - Endpoint: http://j-feature-store-minio:9000

## Configuração de Alta Disponibilidade

### Frontend
- Múltiplas réplicas atrás de um load balancer
- Cache de assets estáticos via CDN

### Backend
- Múltiplas réplicas do FastAPI
- Load balancing via Nginx/Traefik
- Health checks para auto-recuperação

### Databases
- MongoDB: Replica Set com 3 nós
- Redis: Cluster mode com sentinels
- MinIO: Distributed mode com múltiplos nós
