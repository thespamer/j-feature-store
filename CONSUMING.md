# Guia de Consumo da Feature Store

Este guia explica como consumir features da Feature Store através das diferentes interfaces disponíveis.

## Sumário
- [REST API](#rest-api)
- [Exemplos de Uso](#exemplos-de-uso)
- [Melhores Práticas](#melhores-práticas)

## REST API

A Feature Store expõe uma API REST para consumo de features. Todos os endpoints estão disponíveis em `http://localhost:8000/api/v1/`.

### Endpoints Principais

#### 1. Obter Valor Mais Recente de uma Feature
```http
GET /api/v1/features/{feature_id}/latest
```
- Retorna o valor mais recente da feature
- Utiliza cache Redis para baixa latência
- Exemplo de resposta: `42.5`

#### 2. Obter Histórico de Valores
```http
GET /api/v1/features/{feature_id}/history?start_time=2024-01-01T00:00:00Z&end_time=2024-02-01T00:00:00Z
```
- Retorna o histórico de valores para um período
- Parâmetros opcionais:
  - `start_time`: Data inicial (ISO format)
  - `end_time`: Data final (ISO format)
- Exemplo de resposta:
```json
[
  {
    "value": 42.5,
    "timestamp": "2024-01-01T12:00:00Z"
  },
  {
    "value": 43.2,
    "timestamp": "2024-01-02T12:00:00Z"
  }
]
```

#### 3. Listar Features Disponíveis
```http
GET /api/v1/features
```
- Lista todas as features cadastradas
- Parâmetros opcionais:
  - `entity_id`: Filtra features por entidade
- Exemplo de resposta:
```json
[
  {
    "id": "customer_lifetime_value",
    "name": "Customer Lifetime Value",
    "description": "Valor total gasto pelo cliente",
    "data_type": "float",
    "entity_id": "customer",
    "feature_group_id": "customer_metrics"
  }
]
```

#### 4. Obter Feature Específica
```http
GET /api/v1/features/{feature_id}
```
- Retorna detalhes de uma feature específica
- Exemplo de resposta:
```json
{
  "id": "customer_lifetime_value",
  "name": "Customer Lifetime Value",
  "description": "Valor total gasto pelo cliente",
  "data_type": "float",
  "entity_id": "customer",
  "feature_group_id": "customer_metrics"
}
```

## Exemplos de Uso

### Python

```python
import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api/v1"

# Obter valor mais recente
def get_latest_value(feature_id):
    response = requests.get(f"{BASE_URL}/features/{feature_id}/latest")
    return response.json()

# Obter histórico
def get_history(feature_id, days=30):
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)
    
    params = {
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat()
    }
    
    response = requests.get(
        f"{BASE_URL}/features/{feature_id}/history",
        params=params
    )
    return response.json()

# Exemplo de uso
feature_id = "customer_lifetime_value"
latest_value = get_latest_value(feature_id)
history = get_history(feature_id, days=7)
```

### cURL

```bash
# Obter valor mais recente
curl http://localhost:8000/api/v1/features/customer_lifetime_value/latest

# Obter histórico
curl "http://localhost:8000/api/v1/features/customer_lifetime_value/history?start_time=2024-01-01T00:00:00Z&end_time=2024-02-01T00:00:00Z"

# Listar features
curl http://localhost:8000/api/v1/features
```

## Melhores Práticas

1. **Cache**
   - O sistema utiliza Redis como cache
   - Valores recentes são servidos com baixa latência
   - Cache é atualizado automaticamente quando novos valores são inseridos

2. **Batch vs Real-time**
   - Para consultas em tempo real: use o endpoint `/latest`
   - Para análises históricas: use o endpoint `/history`
   - Para treinamento de modelos: considere baixar um período completo de dados

3. **Performance**
   - Limite o período de histórico ao necessário
   - Use paginação quando listar muitas features
   - Considere implementar cache do lado do cliente para valores frequentemente acessados

4. **Monitoramento**
   - Monitor a latência das requisições
   - Observe o hit rate do cache
   - Verifique a frequência de atualização das features

## Próximos Passos

Funcionalidades planejadas para futuras versões:
- SDK Python dedicado
- Suporte a batch serving
- Interface para download de datasets
- Versionamento de features
- Cache configurável por feature
