import requests
import json
from kafka import KafkaProducer
import psycopg2
import time
from datetime import datetime
import os

def test_feature_store():
    # 1. Configurações
    API_URL = os.getenv("API_URL", "http://localhost:8000")
    KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
    POSTGRES_URI = os.getenv("POSTGRES_URI", "postgresql://postgres:postgres@postgres:5432/fstore")
    
    print("Iniciando teste E2E da Feature Store...")
    print(f"API_URL: {API_URL}")
    print(f"KAFKA_BROKER: {KAFKA_BROKER}")
    print(f"POSTGRES_URI: {POSTGRES_URI}")

    # 2. Criar grupo de features
    print("\n1. Criando grupo de features...")
    feature_group = {
        "name": "user_metrics",
        "description": "Métricas de comportamento do usuário",
        "entity_type": "user",
        "tags": ["user", "behavior"],
        "frequency": "daily"
    }
    
    response = requests.post(f"{API_URL}/api/v1/feature-groups", json=feature_group)
    if response.status_code != 200:
        print(f"Erro ao criar grupo de features: {response.text}")
        return
    feature_group_id = response.json()["id"]
    print(f"Grupo de features criado com ID: {feature_group_id}")

    # 3. Criar feature
    print("\n2. Criando feature...")
    feature = {
        "name": "avg_session_duration",
        "description": "Duração média da sessão do usuário",
        "feature_group_id": feature_group_id,
        "entity_id": "user_id",
        "value_type": "float",
        "tags": ["session", "duration"]
    }
    
    response = requests.post(f"{API_URL}/api/v1/features", json=feature)
    if response.status_code != 200:
        print(f"Erro ao criar feature: {response.text}")
        return
    feature_id = response.json()["id"]
    print(f"Feature criada com ID: {feature_id}")

    # 4. Enviar dados para processamento via Kafka
    print("\n3. Enviando dados para processamento...")
    try:
        producer = KafkaProducer(
            bootstrap_servers=[KAFKA_BROKER],
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
        
        event_data = {
            "feature_group": "user_metrics",
            "data": [
                {"user_id": "user1", "session_duration": 120},
                {"user_id": "user1", "session_duration": 180},
                {"user_id": "user2", "session_duration": 90},
                {"user_id": "user2", "session_duration": 150}
            ],
            "transformation": "SQL: SELECT user_id, AVG(session_duration) as avg_session_duration FROM input_data GROUP BY user_id"
        }
        
        producer.send('feature_events', event_data)
        producer.flush()
        print("Dados enviados para o Kafka")
    except Exception as e:
        print(f"Erro ao enviar dados para o Kafka: {str(e)}")
        return

    # 5. Aguardar processamento
    print("\n4. Aguardando processamento...")
    time.sleep(10)

    # 6. Verificar resultados no PostgreSQL
    print("\n5. Verificando resultados...")
    try:
        conn = psycopg2.connect(POSTGRES_URI)
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM features_user_metrics")
        results = cur.fetchall()
        
        print("\nResultados processados:")
        for row in results:
            print(row)
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao verificar resultados no PostgreSQL: {str(e)}")

if __name__ == "__main__":
    test_feature_store()
