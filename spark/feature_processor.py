from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import json
import os
import time
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FeatureProcessor:
    def __init__(self):
        logger.info("Iniciando Feature Processor...")
        
        # Configurar Spark
        self.spark = SparkSession.builder \
            .appName("FeatureProcessor") \
            .config("spark.jars", "/app/postgresql-42.2.18.jar") \
            .getOrCreate()
        
        # Set log level
        self.spark.sparkContext.setLogLevel("WARN")
        logger.info("Spark inicializado com sucesso")
        
        # Configurar propriedades do PostgreSQL
        self.postgres_properties = {
            "url": "jdbc:postgresql://postgres:5432/fstore",
            "driver": "org.postgresql.Driver",
            "user": "postgres",
            "password": "postgres"
        }
        logger.info(f"Postgres URL: {self.postgres_properties['url']}")
        
        # Inicializar o consumidor Kafka com retry
        self.initialize_kafka_consumer()

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=60))
    def initialize_kafka_consumer(self):
        """Inicializa o consumidor Kafka com retry"""
        try:
            kafka_bootstrap_servers = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
            self.consumer = KafkaConsumer(
                'feature_events',
                bootstrap_servers=kafka_bootstrap_servers,
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                auto_offset_reset='latest',
                group_id='feature_processor',
                enable_auto_commit=True,
                # Adicionar configurações de retry e timeout
                session_timeout_ms=30000,
                heartbeat_interval_ms=10000,
                max_poll_interval_ms=300000,
                request_timeout_ms=305000,
                retry_backoff_ms=500,
                reconnect_backoff_ms=1000,
                reconnect_backoff_max_ms=10000
            )
            logger.info("Kafka Consumer inicializado com sucesso")
        except KafkaError as e:
            logger.error(f"Erro ao inicializar Kafka consumer: {e}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def process_message(self, message):
        """Processa uma mensagem do Kafka com retry"""
        try:
            # Processar a mensagem
            event_type = message.get('type')
            feature_data = message.get('data')
            
            if event_type == 'feature_update':
                self.process_feature_update(feature_data)
            elif event_type == 'feature_delete':
                self.process_feature_delete(feature_data)
            else:
                logger.warning(f"Tipo de evento desconhecido: {event_type}")
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            raise

    def create_table_if_not_exists(self, table_name):
        """Criar tabela se não existir"""
        try:
            logger.info(f"Tentando criar tabela {table_name}...")
            
            # Criar DataFrame vazio com schema dinâmico
            schema = StructType([
                StructField("user_id", StringType(), True),
                StructField("avg_session_duration", DoubleType(), True),
                StructField("total_page_views", LongType(), True),
                StructField("processed_at", TimestampType(), True)
            ])
            
            empty_df = self.spark.createDataFrame([], schema)
            
            # Escrever DataFrame vazio para criar tabela
            empty_df.write \
                .format("jdbc") \
                .option("url", "jdbc:postgresql://postgres:5432/fstore") \
                .option("dbtable", table_name) \
                .option("user", "postgres") \
                .option("password", "postgres") \
                .option("driver", "org.postgresql.Driver") \
                .mode("append") \
                .save()
            
            logger.info(f"Tabela {table_name} criada com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar tabela {table_name}: {str(e)}")
            import traceback
            logger.error(f"Stack trace: {traceback.format_exc()}")
            return False

    def save_features(self, features_df, table_name):
        """Salva as features no PostgreSQL"""
        try:
            logger.info(f"Salvando features na tabela {table_name}...")
            features_df.write \
                .format("jdbc") \
                .option("url", "jdbc:postgresql://postgres:5432/fstore") \
                .option("dbtable", table_name) \
                .option("user", "postgres") \
                .option("password", "postgres") \
                .option("driver", "org.postgresql.Driver") \
                .mode("append") \
                .save()
            logger.info(f"Features salvas com sucesso na tabela {table_name}")
        except Exception as e:
            logger.error(f"Erro ao salvar features na tabela {table_name}: {str(e)}")
            logger.error(f"Stack trace: {traceback.format_exc()}")
            raise

    def process_batch_features(self, feature_group, data, transformation):
        """Process batch features using Spark"""
        try:
            logger.info(f"Processando features para grupo: {feature_group}")
            logger.info(f"Dados recebidos: {len(data)} registros")
            logger.info(f"Transformação: {transformation}")
            
            # Converter dados para DataFrame
            input_df = self.spark.createDataFrame(data)
            input_df.createOrReplaceTempView("input_data")
            
            logger.info("DataFrame criado com sucesso")
            logger.info(f"Schema do DataFrame: {input_df.schema.simpleString()}")
            
            # Aplicar transformação
            if transformation.startswith("SQL:"):
                sql = transformation.replace("SQL:", "").strip()
                logger.info(f"Executando SQL: {sql}")
                try:
                    result_df = self.spark.sql(sql)
                    logger.info("SQL executado com sucesso")
                except Exception as e:
                    logger.error(f"Erro ao executar SQL: {str(e)}")
                    raise
            else:
                transform_func = eval(transformation)
                result_df = transform_func(input_df)
            
            logger.info("Transformação aplicada com sucesso")
            logger.info(f"Schema do resultado: {result_df.schema.simpleString()}")
            
            # Adicionar timestamp
            result_df = result_df.withColumn("processed_at", current_timestamp())
            
            # Criar tabela se não existir
            table_name = f"features_{feature_group}"
            if not self.create_table_if_not_exists(table_name):
                raise Exception(f"Falha ao criar tabela {table_name}")
            
            # Salvar resultados
            self.save_features(result_df, table_name)
            
            logger.info(f"Features processadas com sucesso: {result_df.count()} linhas")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao processar features: {str(e)}")
            import traceback
            logger.error(f"Stack trace: {traceback.format_exc()}")
            return False

    def run(self):
        """Executa o processador de features"""
        logger.info("Iniciando processamento de features...")
        
        while True:
            try:
                # Poll for messages
                messages = self.consumer.poll(timeout_ms=1000)
                
                for topic_partition, batch in messages.items():
                    for message in batch:
                        try:
                            data = message.value
                            logger.info(f"Processando mensagem: {data}")
                            self.process_message(data)
                        except Exception as e:
                            logger.error(f"Erro ao processar mensagem {message}: {e}")
                            continue
                
                # Se não houver mensagens, aguarde um pouco
                if not messages:
                    time.sleep(1)
                    
            except KafkaError as e:
                logger.error(f"Erro no Kafka consumer: {e}")
                # Tentar reinicializar o consumer
                try:
                    self.initialize_kafka_consumer()
                except Exception as reinit_error:
                    logger.error(f"Falha ao reinicializar Kafka consumer: {reinit_error}")
                    time.sleep(5)  # Aguardar antes de tentar novamente
            except Exception as e:
                logger.error(f"Erro inesperado: {e}")
                time.sleep(5)  # Aguardar antes de tentar novamente

if __name__ == "__main__":
    processor = FeatureProcessor()
    processor.run()
