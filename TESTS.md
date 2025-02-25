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

## Variáveis de Ambiente

O ambiente de teste usa estas variáveis de ambiente:

```yaml
MONGODB_URI=mongodb://mongodb:27017/fstore
REDIS_URI=redis://redis:6379/0
POSTGRES_URI=postgresql://postgres:postgres@postgres:5432/fstore
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
TESTING=true
```

## Resolução de Problemas

Problemas comuns e soluções:

1. **Erros de Conexão**:
   - Certifique-se de que todos os serviços necessários estão rodando (`docker compose ps`)
   - Verifique os logs dos serviços (`docker compose logs <nome-do-servico>`)

2. **Falhas nos Testes**:
   - Verifique se as variáveis de ambiente estão configuradas corretamente
   - Verifique a conectividade com o banco de dados
   - Certifique-se de que o feature store foi inicializado corretamente

3. **Erros de Importação**:
   - Verifique se o PYTHONPATH está configurado para `/app`
   - Verifique se todas as dependências estão instaladas
   - Certifique-se de que a estrutura do pacote está correta
