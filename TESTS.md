# Guia de Testes

Este documento descreve como executar e escrever testes para o projeto Feature Store.

## Configuração do Ambiente de Testes

O projeto utiliza Docker Compose para criar um ambiente de testes isolado com todas as dependências necessárias:

- MongoDB para armazenamento de features
- Redis para cache
- Kafka para streaming de eventos
- PostgreSQL para armazenamento de metadados

## Executando os Testes

Para executar todos os testes, execute:

```bash
docker compose build backend-test
docker compose run --rm backend-test
```

Isso irá:
1. Construir o container de teste com todas as dependências necessárias
2. Executar a suíte de testes em um ambiente isolado
3. Exibir os resultados dos testes com saída detalhada

## Estrutura dos Testes

### Estrutura de Diretórios

```
backend/
├── tests/
│   ├── conftest.py         # Configuração e fixtures dos testes
│   ├── test_monitoring.py  # Testes para endpoints de monitoramento
│   └── ...                 # Outros arquivos de teste
```

### Configuração dos Testes

O ambiente de testes é configurado em `backend/tests/conftest.py` com:
- Configuração do event loop para testes assíncronos
- Inicialização do feature store
- Configuração das conexões com banco de dados

### Suítes de Teste Disponíveis

#### Testes de Monitoramento (`test_monitoring.py`)

Testa os endpoints de saúde e métricas:

1. Verificação de Saúde (`test_health_check`):
   - Verifica o endpoint `/api/v1/monitoring/health`
   - Checa o status das conexões com MongoDB e Redis
   - Valida o formato da resposta e códigos de status

2. Métricas (`test_metrics`):
   - Testa o endpoint `/api/v1/monitoring/metrics`
   - Verifica as estatísticas do feature store
   - Valida o status de saúde das conexões

## Escrevendo Novos Testes

### Requisitos para Testes

Os testes devem ser escritos usando:
- `pytest` como framework de teste
- `pytest-asyncio` para suporte a testes assíncronos
- `httpx` para cliente HTTP assíncrono

### Exemplo de Teste

```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_exemplo():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/seu-endpoint")
        assert response.status_code == 200
        data = response.json()
        assert "campo_esperado" in data
```

### Boas Práticas

1. Use async/await para todas as operações de banco de dados e HTTP
2. Isole os testes usando fixtures quando necessário
3. Limpe quaisquer dados de teste após a conclusão
4. Use nomes descritivos para os testes e assertions claras
5. Adicione mensagens de erro apropriadas às assertions

## Testes Planejados

### Testes de Integração
- Validar a interação entre os diferentes componentes do sistema
- Testar o fluxo de dados entre o backend e os bancos de dados
- Verificar a integração com Kafka e PostgreSQL

### Testes End-to-End
- Validar o fluxo completo do sistema
- Testar cenários reais de uso
- Verificar a integração entre todos os componentes

### Testes de Performance
- Avaliar o desempenho sob carga
- Medir tempos de resposta
- Identificar gargalos

### Testes de Resiliência
- Verificar recuperação de falhas
- Testar cenários de erro
- Validar mecanismos de retry e fallback

## End-to-End Tests

## Feature Flow Test

O teste end-to-end `test_feature_flow.py` valida o fluxo completo de criação e recuperação de features, garantindo que todos os componentes do sistema estão funcionando corretamente em conjunto.

### Componentes Testados

1. **Backend API**
   - Criação de feature groups
   - Criação de features
   - Armazenamento de valores
   - Recuperação de valores

2. **Feature Processor**
   - Processamento de eventos Kafka
   - Transformação de dados
   - Persistência no PostgreSQL

3. **Bancos de Dados**
   - MongoDB: Armazenamento de metadados
   - PostgreSQL: Armazenamento de valores
   - Redis: Cache de valores

### Fluxo do Teste

1. **Criação de Feature Group**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "name": "test_group",
    "description": "Test group",
    "entity_id": "test_entity",
    "entity_type": "test"
  }' \
  http://localhost:8000/api/v1/feature-groups/
```

2. **Criação de Feature**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "name": "test_feature",
    "description": "Test feature",
    "feature_group_id": "<feature_group_id>",
    "type": "double",
    "entity_id": "test_entity"
  }' \
  http://localhost:8000/api/v1/features/
```

3. **Armazenamento de Valor**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "feature_id": "<feature_id>",
    "entity_id": "test_entity",
    "value": 42.0,
    "timestamp": "2025-02-25T11:17:00Z"
  }' \
  http://localhost:8000/api/v1/features/<feature_id>/values
```

4. **Recuperação de Valor**
```bash
curl http://localhost:8000/api/v1/features/<feature_id>/values/test_entity
```

### Validações

O teste verifica:
1. Criação bem-sucedida de feature groups e features
2. Armazenamento correto de valores no PostgreSQL
3. Cache funcionando no Redis
4. Consistência entre MongoDB e PostgreSQL
5. Processamento correto de eventos pelo Feature Processor

### Executando o Teste

```bash
# Inicia os serviços necessários
docker compose up -d

# Executa o teste
docker compose run --rm e2e-tests pytest e2e/tests/test_feature_flow.py
```

### Troubleshooting

Se o teste falhar, verifique:

1. **Conectividade dos Serviços**
   - PostgreSQL está acessível
   - MongoDB está acessível
   - Redis está acessível
   - Kafka está recebendo mensagens

2. **Logs dos Serviços**
```bash
# Verificar logs do backend
docker compose logs backend

# Verificar logs do feature processor
docker compose logs feature-processor

# Verificar logs do PostgreSQL
docker compose logs postgres
```

3. **Estado dos Dados**
   - Feature existe no MongoDB
   - Feature existe no PostgreSQL
   - Valor está sendo armazenado corretamente
   - Cache está funcionando no Redis

### Problemas Conhecidos

1. **Inicialização dos Serviços**
   - Aguardar PostgreSQL estar pronto antes de iniciar o backend
   - Aguardar Kafka estar pronto antes de iniciar o feature processor

2. **Tipos de Dados**
   - Valores de features devem corresponder ao tipo definido
   - IDs devem ser strings válidas
   - Timestamps devem estar em formato ISO

3. **Cache**
   - Verificar TTL do cache no Redis
   - Garantir consistência entre cache e banco de dados
