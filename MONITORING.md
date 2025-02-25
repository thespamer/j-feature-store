# Monitoramento da Feature Store

Este documento descreve como acessar e utilizar o sistema de monitoramento da Feature Store, que utiliza Prometheus para coletar e visualizar métricas.

## Acessando o Prometheus

O Prometheus está disponível na porta 9090. Para acessar:

1. Inicie os serviços:
   ```bash
   docker compose up -d
   ```

2. Acesse a interface web:
   ```
   http://localhost:9090
   ```

## Configuração do Prometheus

O Prometheus está configurado para coletar métricas dos seguintes endpoints:

1. **Feature Processor** (`:8081/metrics`)
   - Intervalo de coleta: 15s
   - Métricas específicas do processador de features

2. **Spark Metrics** (`:8082/metrics/prometheus`)
   - Intervalo de coleta: 15s
   - Métricas do Apache Spark

A configuração completa pode ser encontrada em `spark/config/prometheus.yml`.

## Métricas Monitoradas

### 1. Feature Processor

#### Performance
- `feature_processor_events_total`: Total de eventos processados
- `feature_processor_processing_time_seconds`: Tempo de processamento por evento
- `feature_processor_batch_size`: Tamanho dos lotes de processamento
- `feature_processor_lag`: Atraso no processamento (diferença entre tempo atual e último evento)

#### Recursos
- `feature_processor_memory_usage_bytes`: Uso de memória
- `feature_processor_cpu_usage_percent`: Uso de CPU
- `feature_processor_disk_usage_bytes`: Uso de disco

#### Erros
- `feature_processor_errors_total`: Total de erros no processamento
- `feature_processor_validation_errors`: Erros de validação de features
- `feature_processor_processing_errors`: Erros durante o processamento

### 2. Apache Spark

#### Executores
- `spark_executor_count`: Número de executores ativos
- `spark_executor_memory_bytes`: Memória utilizada por executor
- `spark_executor_cpu_time_seconds`: Tempo de CPU por executor

#### Jobs
- `spark_job_active_count`: Jobs ativos
- `spark_job_completed_count`: Jobs completados
- `spark_job_failed_count`: Jobs com falha

#### Stages
- `spark_stage_active_count`: Stages ativos
- `spark_stage_completed_count`: Stages completados
- `spark_stage_failed_count`: Stages com falha

### 3. Armazenamento

#### MongoDB
- `mongodb_connections`: Conexões ativas
- `mongodb_ops_total`: Total de operações
- `mongodb_memory_bytes`: Uso de memória

#### Redis
- `redis_connected_clients`: Clientes conectados
- `redis_memory_used_bytes`: Memória utilizada
- `redis_commands_total`: Total de comandos executados

#### PostgreSQL
- `postgres_connections`: Conexões ativas
- `postgres_transactions_total`: Total de transações
- `postgres_blocks_read`: Blocos lidos do disco

## Alertas

O Prometheus está configurado com os seguintes alertas:

1. **Alta Latência**
   - Condição: `feature_processor_processing_time_seconds > 30`
   - Severidade: warning
   - Descrição: Processamento de features está demorando mais que 30 segundos

2. **Erro de Processamento**
   - Condição: `rate(feature_processor_errors_total[5m]) > 0.1`
   - Severidade: critical
   - Descrição: Taxa de erros maior que 10% nos últimos 5 minutos

3. **Uso de Recursos**
   - Condição: `feature_processor_memory_usage_bytes > 80%`
   - Severidade: warning
   - Descrição: Uso de memória acima de 80%

## Queries Úteis

### 1. Taxa de Processamento
```promql
rate(feature_processor_events_total[5m])
```

### 2. Latência Média
```promql
avg_over_time(feature_processor_processing_time_seconds[5m])
```

### 3. Taxa de Erros
```promql
sum(rate(feature_processor_errors_total[5m])) by (type)
```

### 4. Uso de Recursos
```promql
feature_processor_memory_usage_bytes / feature_processor_memory_total_bytes * 100
```

## Dashboards Recomendados

1. **Visão Geral**
   - Taxa de processamento
   - Latência
   - Erros
   - Uso de recursos

2. **Spark**
   - Executores
   - Jobs
   - Stages
   - Memória

3. **Armazenamento**
   - Métricas MongoDB
   - Métricas Redis
   - Métricas PostgreSQL

## Troubleshooting

### Alto Tempo de Processamento
1. Verifique a taxa de eventos no Kafka
2. Monitore o uso de recursos
3. Verifique logs do Feature Processor

### Erros Frequentes
1. Analise os tipos de erros mais comuns
2. Verifique a conectividade com bancos de dados
3. Monitore o estado do cluster Spark

### Problemas de Memória
1. Verifique o garbage collection
2. Monitore o uso de memória por executor
3. Ajuste as configurações de memória se necessário
