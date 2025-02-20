from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from kafka import KafkaConsumer
import json
import os
import time
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FeatureProcessor:
    def __init__(self):
        logger.info("Iniciando Feature Processor...")
        
        # Inicializar Spark
        self.spark = SparkSession.builder \
            .appName("FStore Feature Processor") \
            .config("spark.sql.warehouse.dir", "/tmp/spark-warehouse") \
            .config("spark.jars", "/opt/conda/lib/python3.11/site-packages/pyspark/jars/postgresql-42.6.0.jar") \
            .getOrCreate()
        
        # Set log level
        self.spark.sparkContext.setLogLevel("WARN")
        logger.info("Spark inicializado com sucesso")
        
        # Inicializar conexão com Kafka
        self.consumer = KafkaConsumer(
            'feature_events',
            bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092'),
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset='latest',
            group_id='feature_processor',
            enable_auto_commit=True
        )
        logger.info("Kafka Consumer inicializado com sucesso")
        
        # Inicializar propriedades do Postgres
        self.postgres_properties = {
            "user": "postgres",
            "password": "postgres",
            "driver": "org.postgresql.Driver",
            "url": "jdbc:postgresql://postgres:5432/fstore"
        }
        logger.info(f"Postgres URL: {self.postgres_properties['url']}")

    def create_table_if_not_exists(self, table_name):
        """Criar tabela se não existir"""
        try:
            logger.info(f"Tentando criar tabela {table_name}...")
            
            # Criar DataFrame vazio com schema
            schema = StructType([
                StructField("user_id", StringType(), True),
                StructField("avg_session_duration", DoubleType(), True),
                StructField("processed_at", TimestampType(), True)
            ])
            
            empty_df = self.spark.createDataFrame([], schema)
            
            # Escrever DataFrame vazio para criar tabela
            empty_df.write \
                .jdbc(url=self.postgres_properties["url"],
                     table=table_name,
                     mode="error",
                     properties=self.postgres_properties)
            
            logger.info(f"Tabela {table_name} criada com sucesso")
        except Exception as e:
            if "relation already exists" not in str(e):
                logger.error(f"Erro ao criar tabela {table_name}: {str(e)}")
                raise
            else:
                logger.info(f"Tabela {table_name} já existe")

    def process_batch_features(self, feature_group, data, transformation):
        """Process batch features using Spark"""
        try:
            logger.info(f"Processando features para grupo: {feature_group}")
            logger.info(f"Dados recebidos: {data}")
            logger.info(f"Transformação: {transformation}")
            
            # Converter dados para DataFrame
            input_df = self.spark.createDataFrame(data)
            input_df.createOrReplaceTempView("input_data")
            
            logger.info("DataFrame criado com sucesso")
            logger.info(f"Schema do DataFrame: {input_df.schema}")
            
            # Aplicar transformação
            if transformation.startswith("SQL:"):
                sql = transformation.replace("SQL:", "").strip()
                logger.info(f"Executando SQL: {sql}")
                result_df = self.spark.sql(sql)
            else:
                transform_func = eval(transformation)
                result_df = transform_func(input_df)
            
            logger.info("Transformação aplicada com sucesso")
            logger.info(f"Schema do resultado: {result_df.schema}")
            
            # Adicionar timestamp
            result_df = result_df.withColumn("processed_at", current_timestamp())
            
            # Criar tabela se não existir
            table_name = f"features_{feature_group}"
            self.create_table_if_not_exists(table_name)
            
            # Salvar resultados
            result_df.write \
                .jdbc(url=self.postgres_properties["url"],
                     table=table_name,
                     mode="append",
                     properties=self.postgres_properties)
            
            logger.info(f"Features processadas com sucesso: {result_df.count()} linhas")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao processar features: {str(e)}")
            import traceback
            logger.error(f"Stack trace: {traceback.format_exc()}")
            return False

    def run(self):
        """Loop principal de processamento"""
        logger.info("Iniciando loop de processamento...")
        
        while True:
            try:
                # Consumir mensagens do Kafka
                logger.info("Aguardando mensagens do Kafka...")
                for message in self.consumer:
                    try:
                        event_data = message.value
                        logger.info(f"Recebido evento: {event_data}")
                        
                        success = self.process_batch_features(
                            event_data["feature_group"],
                            event_data["data"],
                            event_data["transformation"]
                        )
                        
                        if success:
                            logger.info("Evento processado com sucesso")
                        else:
                            logger.error("Falha ao processar evento")
                            
                    except Exception as e:
                        logger.error(f"Erro ao processar mensagem: {str(e)}")
                        import traceback
                        logger.error(f"Stack trace: {traceback.format_exc()}")
                        continue
                        
            except Exception as e:
                logger.error(f"Erro no loop principal: {str(e)}")
                import traceback
                logger.error(f"Stack trace: {traceback.format_exc()}")
                time.sleep(5)  # Esperar um pouco antes de tentar novamente

if __name__ == "__main__":
    processor = FeatureProcessor()
    processor.run()
