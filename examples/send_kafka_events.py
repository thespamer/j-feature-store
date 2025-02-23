from kafka import KafkaProducer
import json
import time
from datetime import datetime
import random

def send_feature_events():
    # Inicializar o produtor Kafka
    producer = KafkaProducer(
        bootstrap_servers='kafka:9092',
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )

    # Dados de exemplo para processamento
    sample_data = [
        {
            "user_id": f"user_{i}",
            "session_duration": random.uniform(60, 3600),  # Entre 1 min e 1 hora
            "page_views": random.randint(1, 50)
        }
        for i in range(1000)
    ]

    # Transformação SQL para calcular métricas agregadas
    transformation = """SELECT 
        user_id,
        AVG(session_duration) as avg_session_duration,
        SUM(page_views) as total_page_views
    FROM input_data
    GROUP BY user_id"""

    # Criar evento
    event = {
        "feature_group": "user_metrics",
        "data": sample_data,
        "transformation": "SQL:" + transformation
    }

    try:
        # Enviar evento
        producer.send('feature_events', event)
        producer.flush()
        print("Evento enviado com sucesso!")
        print(f"Dados: {len(sample_data)} registros")
        print(f"Transformação: {transformation}")
    except Exception as e:
        print(f"Erro ao enviar evento: {e}")
    finally:
        producer.close()

if __name__ == "__main__":
    print("Enviando eventos para processamento Spark...")
    send_feature_events()
