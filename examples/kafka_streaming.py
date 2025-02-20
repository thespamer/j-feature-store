from fstore import FeatureStore
from fstore.connectors import KafkaConnector
import json

# Inicializar o Feature Store
store = FeatureStore()

# Configurar o conector Kafka
kafka_config = {
    "bootstrap_servers": "localhost:9092",
    "group_id": "feature_store_group",
    "auto_offset_reset": "latest"
}

# Criar uma conexão com Kafka
connector = KafkaConnector(kafka_config)

# Registrar uma feature de streaming do Kafka
feature = store.create_feature(
    name="customer_last_action",
    description="Última ação realizada pelo cliente na plataforma",
    entity_id="customer_id",
    feature_group="customer_behavior",
    type="categorical",
    stream_config={
        "topic": "customer_events",
        "value_field": "action",
        "timestamp_field": "event_timestamp"
    }
)

# Configurar o processamento de streaming
def process_event(event):
    try:
        data = json.loads(event)
        return {
            "entity_id": data["customer_id"],
            "value": data["action"],
            "timestamp": data["event_timestamp"]
        }
    except Exception as e:
        print(f"Erro ao processar evento: {e}")
        return None

# Iniciar o processamento de streaming
store.start_streaming_feature(
    feature_name="customer_last_action",
    connector=connector,
    process_fn=process_event
)

# Para parar o streaming quando necessário
# store.stop_streaming_feature("customer_last_action")
