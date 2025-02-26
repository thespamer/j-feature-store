import pytest
import time
import json
from typing import Dict, Any
from datetime import datetime, timedelta

import requests
from kafka import KafkaProducer, KafkaConsumer
import redis
import pandas as pd
from pymongo import MongoClient

from app.core.config import settings

class TestE2EFeatureStore:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Configura o ambiente para os testes"""
        # Aguarda todos os serviços estarem prontos
        self.wait_for_services()
        
        # Inicializa conexões
        self.api_url = "http://localhost:8000"
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL)
        self.mongo_client = MongoClient(settings.MONGODB_URI)
        self.kafka_producer = KafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        yield
        
        # Limpeza após os testes
        self.cleanup()

    def wait_for_services(self, timeout=60):
        """Aguarda todos os serviços estarem disponíveis"""
        services = {
            "api": lambda: requests.get(f"{self.api_url}/health").status_code == 200,
            "redis": lambda: self.redis_client.ping(),
            "mongodb": lambda: self.mongo_client.admin.command('ping')['ok'] == 1,
            "kafka": lambda: len(self.kafka_producer.bootstrap_connected()) > 0
        }
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            if all(check() for check in services.values()):
                return
            time.sleep(1)
        raise TimeoutError("Timeout esperando serviços iniciarem")

    def cleanup(self):
        """Limpa dados de teste"""
        self.redis_client.flushall()
        self.mongo_client.drop_database('test_db')
        self.kafka_producer.close()

    def test_complete_feature_workflow(self):
        """Testa o fluxo completo de uma feature"""
        # 1. Criar uma feature
        feature_data = {
            "name": "user_purchase_amount",
            "description": "Valor total de compras do usuário",
            "type": "numeric",
            "metadata": {
                "owner": "e2e_test",
                "team": "data_science",
                "tags": ["e2e", "test", "purchase"]
            }
        }
        
        response = requests.post(
            f"{self.api_url}/api/v1/features",
            json=feature_data
        )
        assert response.status_code == 201
        feature = response.json()
        feature_id = feature["id"]

        # 2. Enviar dados via Kafka
        user_purchases = [
            {"user_id": "user1", "amount": 100.0},
            {"user_id": "user1", "amount": 150.0},
            {"user_id": "user2", "amount": 75.0}
        ]
        
        for purchase in user_purchases:
            self.kafka_producer.send(
                'purchase_events',
                {
                    "feature_id": feature_id,
                    "entity_id": purchase["user_id"],
                    "value": purchase["amount"],
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        self.kafka_producer.flush()

        # 3. Aguardar processamento
        time.sleep(5)  # Tempo para processamento

        # 4. Verificar valores via API
        response = requests.get(
            f"{self.api_url}/api/v1/features/{feature_id}/values/user1"
        )
        assert response.status_code == 200
        values = response.json()
        assert len(values) == 2
        assert sum(v["value"] for v in values) == 250.0

        # 5. Verificar cache Redis
        cache_key = f"feature:{feature_id}:user1"
        cached_value = self.redis_client.get(cache_key)
        assert cached_value is not None

        # 6. Verificar armazenamento MongoDB
        db = self.mongo_client.get_database('feature_store')
        stored_values = list(db.feature_values.find({
            "feature_id": feature_id,
            "entity_id": "user1"
        }))
        assert len(stored_values) == 2

    def test_batch_processing(self):
        """Testa processamento em batch de features"""
        # 1. Criar feature para teste em batch
        feature_data = {
            "name": "user_activity_score",
            "description": "Score de atividade do usuário",
            "type": "numeric"
        }
        
        response = requests.post(
            f"{self.api_url}/api/v1/features",
            json=feature_data
        )
        feature_id = response.json()["id"]

        # 2. Criar DataFrame com dados
        data = {
            "user_id": ["user1", "user2", "user3"],
            "activity_score": [0.8, 0.6, 0.9]
        }
        df = pd.DataFrame(data)

        # 3. Enviar para processamento em batch
        batch_data = []
        for _, row in df.iterrows():
            batch_data.append({
                "feature_id": feature_id,
                "entity_id": row["user_id"],
                "value": row["activity_score"],
                "timestamp": datetime.utcnow().isoformat()
            })

        response = requests.post(
            f"{self.api_url}/api/v1/features/batch",
            json={"values": batch_data}
        )
        assert response.status_code == 201

        # 4. Verificar processamento
        time.sleep(5)  # Aguarda processamento

        # 5. Verificar valores processados
        for user_id in data["user_id"]:
            response = requests.get(
                f"{self.api_url}/api/v1/features/{feature_id}/values/{user_id}"
            )
            assert response.status_code == 200
            values = response.json()
            assert len(values) == 1

    def test_feature_serving(self):
        """Testa o serving de features"""
        # 1. Criar múltiplas features
        features = [
            {"name": "user_age", "type": "numeric"},
            {"name": "user_location", "type": "categorical"},
            {"name": "last_purchase_date", "type": "temporal"}
        ]
        
        feature_ids = []
        for feature_data in features:
            response = requests.post(
                f"{self.api_url}/api/v1/features",
                json=feature_data
            )
            feature_ids.append(response.json()["id"])

        # 2. Inserir valores para um usuário
        user_id = "test_user"
        values = [
            {"value": 25},
            {"value": "São Paulo"},
            {"value": datetime.utcnow().isoformat()}
        ]
        
        for feature_id, value in zip(feature_ids, values):
            requests.post(
                f"{self.api_url}/api/v1/features/{feature_id}/values/{user_id}",
                json=value
            )

        # 3. Testar serving de feature vector
        response = requests.get(
            f"{self.api_url}/api/v1/serving/vector",
            params={
                "entity_id": user_id,
                "feature_ids": ",".join(feature_ids)
            }
        )
        assert response.status_code == 200
        vector = response.json()
        assert len(vector) == len(features)

    def test_error_handling(self):
        """Testa o tratamento de erros"""
        # 1. Tentar criar feature com dados inválidos
        invalid_feature = {
            "name": "invalid feature name with spaces",
            "type": "invalid_type"
        }
        
        response = requests.post(
            f"{self.api_url}/api/v1/features",
            json=invalid_feature
        )
        assert response.status_code == 422

        # 2. Tentar acessar feature inexistente
        response = requests.get(
            f"{self.api_url}/api/v1/features/nonexistent"
        )
        assert response.status_code == 404

        # 3. Tentar inserir valor com tipo errado
        feature_data = {"name": "test_feature", "type": "numeric"}
        response = requests.post(
            f"{self.api_url}/api/v1/features",
            json=feature_data
        )
        feature_id = response.json()["id"]
        
        invalid_value = {"value": "not a number"}
        response = requests.post(
            f"{self.api_url}/api/v1/features/{feature_id}/values/test_user",
            json=invalid_value
        )
        assert response.status_code == 422

    def test_monitoring(self):
        """Testa funcionalidades de monitoramento"""
        # 1. Verificar health check
        response = requests.get(f"{self.api_url}/health")
        assert response.status_code == 200
        health = response.json()
        assert health["status"] == "healthy"

        # 2. Verificar métricas Prometheus
        response = requests.get(f"{self.api_url}/metrics")
        assert response.status_code == 200
        metrics = response.text
        assert "feature_store" in metrics

        # 3. Gerar algumas métricas
        for _ in range(10):
            requests.get(f"{self.api_url}/api/v1/features")
        
        # 4. Verificar métricas atualizadas
        response = requests.get(f"{self.api_url}/metrics")
        assert response.status_code == 200
        updated_metrics = response.text
        assert "http_requests_total" in updated_metrics
