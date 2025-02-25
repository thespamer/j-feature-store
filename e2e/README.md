# Testes End-to-End

Este diretório contém os testes end-to-end (e2e) para o Feature Store. Os testes e2e validam o fluxo completo da aplicação, garantindo que todos os componentes trabalhem juntos corretamente.

## Estrutura

```
e2e/
├── Dockerfile.e2e           # Dockerfile para executar os testes
├── docker-compose.e2e.yml   # Configuração do ambiente de teste
├── requirements.e2e.txt     # Dependências dos testes
└── tests/
    ├── conftest.py         # Configurações e fixtures
    └── test_feature_flow.py # Testes do fluxo completo
```

## Características

1. **Ambiente Isolado**: 
   - Usa bancos de dados separados para testes (sufixo `_e2e`)
   - Tópicos Kafka com prefixo `e2e_test`
   - Não interfere com ambiente de desenvolvimento ou produção

2. **Componentes Testados**:
   - Backend API
   - Feature Processor
   - Integrações com MongoDB, Redis, Kafka e PostgreSQL

3. **Fluxos Testados**:
   - Criação de grupos de features
   - Criação de features
   - Processamento de eventos
   - Consulta de valores
   - Monitoramento e health checks

## Executando os Testes

```bash
# Construir e executar os testes e2e
docker compose -f docker-compose.yml -f e2e/docker-compose.e2e.yml up --build e2e-tests

# Executar testes específicos
docker compose -f docker-compose.yml -f e2e/docker-compose.e2e.yml run --rm e2e-tests pytest -v e2e/tests/test_feature_flow.py -k "test_complete_feature_flow"

# Ver logs detalhados
docker compose -f docker-compose.yml -f e2e/docker-compose.e2e.yml run --rm e2e-tests pytest -v --log-cli-level=INFO
```

## Boas Práticas

1. **Isolamento**:
   - Sempre use os bancos de dados e tópicos de teste
   - Limpe os dados após os testes
   - Evite interferir com outros ambientes

2. **Resiliência**:
   - Use retry para operações que podem falhar
   - Adicione timeouts apropriados
   - Valide estados intermediários

3. **Manutenção**:
   - Mantenha os testes focados em fluxos completos
   - Documente os cenários testados
   - Atualize os testes quando a API mudar
