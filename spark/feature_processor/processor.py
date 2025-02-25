from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import json
import os
import time
import logging
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential
from prometheus_client import Counter, Histogram, Gauge, start_http_server, REGISTRY, CollectorRegistry

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Métricas Prometheus
registry = CollectorRegistry()
EVENTS_PROCESSED = Counter('feature_processor_events_processed_total', 'Total de eventos processados', registry=registry)
PROCESSING_ERRORS = Counter('feature_processor_errors_total', 'Total de erros de processamento', registry=registry)
PROCESSING_TIME = Histogram('feature_processor_processing_seconds', 'Tempo de processamento dos eventos', registry=registry)
BATCH_SIZE = Histogram('feature_processor_batch_size', 'Tamanho dos batches processados', registry=registry)
KAFKA_LAG = Gauge('feature_processor_kafka_lag', 'Lag do consumidor Kafka', registry=registry)

class FeatureProcessor:
    def __init__(self):
        logger.info("Iniciando Feature Processor...")
        
        # Iniciar servidor de métricas
        start_http_server(8081, registry=registry)
        logger.info("Servidor de métricas iniciado na porta 8081")
        
        # Configurar Spark com otimizações
        self.spark = SparkSession.builder \
            .appName("FeatureProcessor") \
            .config("spark.jars", "/app/postgresql-42.2.18.jar") \
            .config("spark.sql.shuffle.partitions", "2") \
            .config("spark.default.parallelism", "2") \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .config("spark.dynamicAllocation.enabled", "false") \
            .config("spark.executor.instances", "1") \
            .config("spark.executor.memory", "1g") \
            .config("spark.driver.memory", "1g") \
            .getOrCreate()
        
        # Set log level
        self.spark.sparkContext.setLogLevel("WARN")
        logger.info("Spark inicializado com sucesso")
        
        # Métricas internas
        self._processing_start_time = None
        self._last_processed_offset = 0
        
        # Configurar propriedades do PostgreSQL
        self.postgres_url = f"jdbc:postgresql://{os.getenv('POSTGRES_HOST', 'postgres')}:{os.getenv('POSTGRES_PORT', 5432)}/{os.getenv('POSTGRES_DB', 'fstore')}"
        self.postgres_properties = {
            "driver": "org.postgresql.Driver",
            "user": os.getenv("POSTGRES_USER", "postgres"),
            "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
            "batchsize": "1000"  
        }
        
        # Inicializar consumidor Kafka com retry
        self._init_kafka_consumer()

    def _init_kafka_consumer(self):
        """Inicializa o consumidor Kafka com retry"""
        max_retries = 3
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                self.kafka_consumer = KafkaConsumer(
                    'feature_events',
                    bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092'),
                    group_id='feature_processor',
                    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                    auto_offset_reset='latest',
                    enable_auto_commit=True,
                    max_poll_records=100,  
                    fetch_max_wait_ms=500  
                )
                logger.info("Consumidor Kafka inicializado com sucesso")
                return
            except KafkaError as e:
                if attempt == max_retries - 1:
                    logger.error(f"Erro ao inicializar consumidor Kafka: {e}")
                    raise
                logger.warning(f"Tentativa {attempt + 1} falhou, tentando novamente em {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= 2

    @PROCESSING_TIME.time()
    def process_event(self, event):
        """Processa um único evento"""
        try:
            if not isinstance(event, dict):
                event = json.loads(event)
            
            # Validar evento
            required_fields = ['feature_id', 'entity_id', 'value', 'timestamp']
            if not all(field in event for field in required_fields):
                raise KeyError(f"Campos obrigatórios faltando. Necessários: {required_fields}")
            
            logger.info(f"Processando evento: {event}")
            
            # Cache schema para reutilização
            if not hasattr(self, '_event_schema'):
                self._event_schema = StructType([
                    StructField("feature_id", StringType(), False),
                    StructField("entity_id", StringType(), False),
                    StructField("value", DoubleType(), False),
                    StructField("timestamp", LongType(), False)
                ])

            # Converte o evento em DataFrame
            event_df = self.spark.createDataFrame([event], schema=self._event_schema)

            # Salva no PostgreSQL
            event_df.write \
                .mode("append") \
                .jdbc(url=self.postgres_url, table="feature_values", properties=self.postgres_properties)

            EVENTS_PROCESSED.inc()
            logger.info(f"Evento processado com sucesso: {event}")
            
        except Exception as e:
            PROCESSING_ERRORS.inc()
            logger.error(f"Erro ao processar evento: {e}")
            raise
    
    def health_check(self):
        """Verifica a saúde do processador"""
        health = {
            "status": "healthy",
            "spark": self._check_spark_health(),
            "kafka": self._check_kafka_health(),
            "postgres": self._check_postgres_health(),
            "metrics": {
                "events_processed": EVENTS_PROCESSED._value.get(),
                "processing_errors": PROCESSING_ERRORS._value.get(),
                "current_kafka_lag": KAFKA_LAG._value.get()
            },
            "timestamp": datetime.now().isoformat()
        }
        return health
    
    def _check_spark_health(self):
        """Verifica a saúde do Spark"""
        try:
            # Executar query simples para testar
            self.spark.sql("SELECT 1").collect()
            return {"status": "healthy"}
        except Exception as e:
            logger.error(f"Erro no health check do Spark: {e}")
            return {"status": "unhealthy", "error": str(e)}
    
    def _check_kafka_health(self):
        """Verifica a saúde do Kafka"""
        try:
            partitions = self.kafka_consumer.partitions_for_topic('feature_events')
            if not partitions:
                return {"status": "unhealthy", "error": "Tópico não encontrado"}
            return {"status": "healthy", "partitions": len(partitions)}
        except Exception as e:
            logger.error(f"Erro no health check do Kafka: {e}")
            return {"status": "unhealthy", "error": str(e)}
    
    def _check_postgres_health(self):
        """Verifica a saúde do PostgreSQL"""
        try:
            # Tentar ler uma linha do PostgreSQL
            self.spark.read \
                .jdbc(url=self.postgres_url, table="(SELECT 1) AS tmp", properties=self.postgres_properties) \
                .load()
            return {"status": "healthy"}
        except Exception as e:
            logger.error(f"Erro no health check do PostgreSQL: {e}")
            return {"status": "unhealthy", "error": str(e)}
    
    def process_batch(self, df, feature_id):
        """Processa um batch de dados"""
        try:
            batch_size = df.count()
            BATCH_SIZE.observe(batch_size)
            
            # Adicionar feature_id e timestamp
            df = df.withColumn("feature_id", lit(feature_id)) \
                   .withColumn("timestamp", current_timestamp())
            
            # Salvar no PostgreSQL
            df.write \
                .jdbc(url=f"jdbc:postgresql://{os.getenv('POSTGRES_HOST', 'postgres')}:{os.getenv('POSTGRES_PORT', 5432)}/{os.getenv('POSTGRES_DB', 'fstore')}", table="feature_values", properties=self.postgres_properties) \
                .mode("append") \
                .save()
            
            EVENTS_PROCESSED.inc(batch_size)
            logger.info(f"Batch processado com sucesso: {feature_id}, {batch_size} registros")
            return True
            
        except Exception as e:
            PROCESSING_ERRORS.inc()
            logger.error(f"Erro ao processar batch: {e}")
            raise
    
    def process_kafka_messages(self, max_messages=None):
        """Processa mensagens do Kafka"""
        messages_processed = 0
        
        try:
            for message in self.kafka_consumer:
                # Atualizar métricas de lag
                current_offset = message.offset
                KAFKA_LAG.set(current_offset - self._last_processed_offset)
                
                # Processar mensagem
                self.process_event(message.value)
                
                self._last_processed_offset = current_offset
                messages_processed += 1
                
                if max_messages and messages_processed >= max_messages:
                    break
                    
        except Exception as e:
            logger.error(f"Erro ao processar mensagens do Kafka: {e}")
            raise
            
    def run(self):
        """Executa o processador"""
        logger.info("Iniciando processamento...")
        try:
            self.process_kafka_messages()
        except Exception as e:
            logger.error(f"Erro no loop principal: {e}")
            raise

if __name__ == "__main__":
    processor = FeatureProcessor()
    processor.run()
