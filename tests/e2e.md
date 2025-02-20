# Testes End-to-End (E2E) da Feature Store

Este documento descreve como executar os testes end-to-end da Feature Store, que validam a integração entre todos os componentes do sistema.

## Pré-requisitos

- Docker
- Docker Compose

## Componentes Testados

O teste E2E valida a integração dos seguintes componentes:

1. **Backend (FastAPI)**
   - Criação de grupos de features
   - Criação de features individuais

2. **Kafka**
   - Envio de eventos para processamento
   - Consumo de eventos pelo processador

3. **Feature Processor (PySpark)**
   - Processamento de dados usando Spark SQL
   - Transformação e agregação de features

4. **PostgreSQL**
   - Armazenamento dos resultados processados
   - Persistência das features calculadas

## Como Executar os Testes

1. **Iniciar os Serviços**
   ```bash
   docker-compose up --build -d
   ```
   Este comando irá:
   - Construir todas as imagens Docker necessárias
   - Iniciar todos os serviços em background
   - Configurar as conexões entre os serviços

2. **Executar o Teste E2E**
   ```bash
   docker-compose run e2e-test
   ```
   Este comando irá:
   - Criar um grupo de features de exemplo
   - Criar uma feature de duração média de sessão
   - Enviar dados de exemplo para processamento
   - Verificar os resultados no PostgreSQL

## Estrutura do Teste

O teste E2E (`e2e_test.py`) executa os seguintes passos:

1. **Criação de Grupo de Features**
   - Nome: user_metrics
   - Descrição: Métricas de comportamento do usuário
   - Tipo de entidade: user

2. **Criação de Feature**
   - Nome: avg_session_duration
   - Descrição: Duração média da sessão do usuário
   - Grupo: user_metrics

3. **Envio de Dados**
   - Envia dados de exemplo para o Kafka
   - Os dados incluem durações de sessão para diferentes usuários

4. **Verificação de Resultados**
   - Aguarda o processamento dos dados
   - Verifica os resultados na tabela PostgreSQL
   - Valida as médias calculadas por usuário

## Resultados Esperados

O teste é considerado bem-sucedido quando:

1. O grupo de features é criado com sucesso
2. A feature é criada e associada ao grupo
3. Os dados são processados corretamente
4. Os resultados no PostgreSQL mostram:
   - Médias corretas por usuário
   - Timestamp de processamento
   - Dados consistentes com a transformação aplicada

## Troubleshooting

Se o teste falhar, verifique:

1. **Logs dos Serviços**
   ```bash
   docker-compose logs -f feature-processor  # Logs do processador
   docker-compose logs -f backend            # Logs do backend
   docker-compose logs -f kafka              # Logs do Kafka
   ```

2. **Estado dos Containers**
   ```bash
   docker-compose ps  # Lista status dos containers
   ```

3. **Conectividade**
   - Verifique se todos os serviços estão rodando
   - Confirme que as portas estão acessíveis
   - Verifique as configurações de rede no docker-compose.yml
