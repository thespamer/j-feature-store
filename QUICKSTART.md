# Guia Rápido - FStore

## Pré-requisitos

- Docker e Docker Compose
- Git
- Python 3.9+ (para desenvolvimento local)
- Node.js 16+ (para desenvolvimento local)

## 1. Configuração Inicial

```bash
# Clone o repositório
git clone <repository_url>
cd fstore

# Crie o arquivo .env com as variáveis de ambiente
cat > .env << EOL
POSTGRES_DB=fstore
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
MONGODB_URI=mongodb://mongodb:27017/fstore
REDIS_URI=redis://redis:6379/0
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
EOL
```

## 2. Iniciar a Plataforma

```bash
# Construir e iniciar todos os serviços
docker-compose up -d

# Verificar se todos os serviços estão rodando
docker-compose ps
```

## 3. Executar Migrações

```bash
# Executar migrações do banco de dados
docker-compose exec postgres psql -U postgres -d fstore -f /app/migrations/V1__initial.sql
```

## 4. Verificar os Serviços

Após iniciar, verifique se os serviços estão disponíveis:

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Spark UI: http://localhost:4040
- Métricas: http://localhost:8000/metrics

## 5. Testar a API

### 5.1. Criar uma Feature

```bash
curl -X POST http://localhost:8000/api/v1/features/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "customer_lifetime_value",
    "description": "Total value of customer purchases",
    "source": {
      "type": "postgresql",
      "query": "SELECT customer_id, SUM(value) FROM orders GROUP BY customer_id",
      "update_frequency": "1h"
    },
    "tags": ["customer", "financial"],
    "owner": "data_team"
  }'
```

### 5.2. Listar Features

```bash
curl http://localhost:8000/api/v1/features/
```

### 5.3. Inserir Valores

```bash
curl -X POST http://localhost:8000/api/v1/features/customer_lifetime_value/values \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "customer_123",
    "value": 1000.50
  }'
```

### 5.4. Consultar Valores

```bash
curl http://localhost:8000/api/v1/features/customer_lifetime_value/values?entity_id=customer_123
```

## 6. Testar Conectores

### 6.1. PostgreSQL

```bash
# Criar tabela de exemplo
docker-compose exec postgres psql -U postgres -d fstore -c "
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    customer_id VARCHAR(255),
    value DECIMAL
);"

# Inserir dados de exemplo
docker-compose exec postgres psql -U postgres -d fstore -c "
INSERT INTO orders (customer_id, value) VALUES 
    ('customer_123', 100.50),
    ('customer_123', 200.75),
    ('customer_456', 150.25);"
```

### 6.2. MongoDB

```bash
# Inserir documento de exemplo
docker-compose exec mongodb mongosh --eval '
db.user_features.insertMany([
    {
        customer_id: "customer_123",
        features: {
            last_login: ISODate(),
            session_count: 10
        }
    }
])'
```

### 6.3. Kafka

```bash
# Produzir mensagem de exemplo
docker-compose exec kafka kafka-console-producer \
  --bootstrap-server kafka:9092 \
  --topic user_events \
  --property "parse.key=true" \
  --property "key.separator=:" << EOL
customer_123:{"event_type": "purchase", "value": 50.25}
EOL
```

## 7. Monitoramento

### 7.1. Verificar Métricas

```bash
# Métricas gerais
curl http://localhost:8000/metrics

# Métricas específicas
curl http://localhost:8000/metrics | grep fstore_feature
```

### 7.2. Verificar Logs

```bash
# Logs do backend
docker-compose logs -f backend

# Logs do frontend
docker-compose logs -f frontend

# Logs do Spark
docker-compose logs -f spark
```

## 8. Desenvolvimento Local

Para desenvolvimento local sem Docker:

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # ou `venv\Scripts\activate` no Windows
pip install -r requirements.txt
pip install -r requirements-dev.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm start
```

## 9. Executar Testes

```bash
# Testes do backend
cd backend
pytest tests/ --cov=app

# Testes do frontend
cd frontend
npm test
```

## 10. Troubleshooting

### Problemas Comuns

1. **Serviços não iniciam**
   ```bash
   # Verificar logs
   docker-compose logs -f
   
   # Reiniciar serviços
   docker-compose down
   docker-compose up -d
   ```

2. **Erro de conexão com banco de dados**
   ```bash
   # Verificar status dos bancos
   docker-compose ps postgres mongodb redis
   
   # Verificar logs específicos
   docker-compose logs postgres
   ```

3. **Problemas com Kafka**
   ```bash
   # Verificar tópicos
   docker-compose exec kafka kafka-topics --list --bootstrap-server kafka:9092
   
   # Verificar status do Zookeeper
   docker-compose logs zookeeper
   ```

### Comandos Úteis

```bash
# Reiniciar um serviço específico
docker-compose restart backend

# Limpar todos os dados
docker-compose down -v

# Verificar uso de recursos
docker stats
```

## 11. Próximos Passos

1. Configure autenticação e autorização
2. Adicione mais features
3. Configure backups
4. Implemente mais validações de dados
5. Adicione dashboards de monitoramento

Para mais informações, consulte:
- [Documentação da API](docs/API.md)
- [Guia de Conectores](docs/DATA_SOURCES.md)
- [Arquitetura](ARCHITECTURE.md)
