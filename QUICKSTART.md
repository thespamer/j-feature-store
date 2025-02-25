# Guia de Início Rápido

## Pré-requisitos
- Docker e Docker Compose
- Python 3.8 ou superior
- curl (para exemplos de API)

## Instalação

1. **Clone o Repositório**
```bash
git clone https://github.com/yourusername/feature-store.git
cd feature-store
```

2. **Configure as Variáveis de Ambiente**
```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações:

```env
# PostgreSQL
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=fstore
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# MongoDB
MONGODB_URI=mongodb://mongodb:27017
MONGODB_DB=fstore

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_TOPIC=feature_events
```

3. **Inicie os Serviços**
```bash
docker compose up -d
```

## Uso Básico

### 1. Criar um Grupo de Features
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "name": "user_features",
    "description": "Métricas de comportamento do usuário",
    "entity_id": "user_id",
    "entity_type": "user"
  }' \
  http://localhost:8000/api/v1/feature-groups/
```

### 2. Criar uma Feature
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "name": "purchase_count",
    "description": "Número de compras",
    "feature_group_id": "<id_do_grupo>",
    "type": "double",
    "entity_id": "user_id"
  }' \
  http://localhost:8000/api/v1/features/
```

### 3. Armazenar um Valor de Feature
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "feature_id": "<id_da_feature>",
    "entity_id": "user123",
    "value": 42.0,
    "timestamp": "2025-02-25T11:17:00Z"
  }' \
  http://localhost:8000/api/v1/features/<id_da_feature>/values
```

### 4. Recuperar um Valor de Feature
```bash
curl http://localhost:8000/api/v1/features/<id_da_feature>/values/user123
```

## Verificação dos Serviços

### Status dos Containers
```bash
docker compose ps
```

### Logs dos Serviços
```bash
# Backend
docker compose logs backend

# Processador de Features
docker compose logs feature-processor

# PostgreSQL
docker compose logs postgres
```

## Resolução de Problemas

### 1. Problemas de Conexão

Se houver problemas de conexão, verifique:
- Os serviços estão rodando? (`docker compose ps`)
- As variáveis de ambiente estão corretas? (`.env`)
- Os logs mostram algum erro? (`docker compose logs`)

### 2. Erros Comuns

#### Erro 500 na API
- Verifique os logs do backend
- Confirme se o MongoDB e PostgreSQL estão acessíveis
- Verifique se as migrations foram aplicadas

#### Dados Não Aparecem
- Verifique os logs do processador de features
- Confirme se o Kafka está recebendo mensagens
- Verifique se o PostgreSQL está armazenando os dados

#### Problemas de Cache
- Verifique se o Redis está rodando
- Confirme se a conexão com Redis está correta
- Verifique os logs de cache no backend

## Desenvolvimento

### Ambiente de Desenvolvimento
```bash
# Instalar dependências de desenvolvimento
pip install -r requirements-dev.txt

# Executar testes
docker compose run --rm e2e-tests pytest

# Verificar cobertura de código
docker compose run --rm backend-test pytest --cov=app
```

### Comandos Úteis

```bash
# Reiniciar todos os serviços
docker compose down && docker compose up -d

# Limpar todos os dados
docker compose down -v

# Reconstruir imagens
docker compose build --no-cache
```

## Próximos Passos

1. Explore a [documentação da arquitetura](ARCHITECTURE.md)
2. Veja os [testes](TESTS.md) para entender o comportamento do sistema
3. Configure monitoramento com Prometheus e Grafana
4. Implemente autenticação e autorização
5. Adicione mais features e transformadores
