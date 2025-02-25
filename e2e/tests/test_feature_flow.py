import pytest
from httpx import AsyncClient
from kafka import KafkaProducer, KafkaConsumer
import time
import json

@pytest.mark.asyncio
async def test_complete_feature_flow(
    kafka_producer: KafkaProducer,
    kafka_consumer: KafkaConsumer
):
    """
    Teste end-to-end do fluxo completo de features:
    1. Criar um grupo de features
    2. Criar uma feature
    3. Enviar eventos para o Kafka
    4. Verificar se os eventos foram processados
    5. Consultar os valores da feature
    """
    async with AsyncClient(base_url="http://backend:8000", follow_redirects=True) as client:
        # 1. Criar grupo de features
        feature_group_data = {
            "name": "e2e_test_group",
            "description": "Grupo de features para teste e2e",
            "entity_id": "test_entity",
            "entity_type": "user",
            "tags": ["test", "e2e"]
        }
        response = await client.post("/api/v1/feature-groups/", json=feature_group_data)
        assert response.status_code == 200  # API returns 200 for successful creation
        feature_group = response.json()
        
        # 2. Criar feature
        feature_data = {
            "name": "e2e_test_feature",
            "description": "Feature para teste e2e",
            "feature_group_id": feature_group["id"],
            "type": "float",
            "entity_id": "test_entity",
            "tags": ["test", "e2e"]
        }
        response = await client.post("/api/v1/features/", json=feature_data)
        assert response.status_code == 200  # API returns 200 for successful creation
        feature = response.json()
        
        # 3. Enviar eventos para o Kafka
        event = {
            "feature_id": feature["id"],  # Use feature ID instead of name
            "entity_id": "test_entity",
            "value": 42.0,  # Simplified event format
            "timestamp": int(time.time())
        }
        kafka_producer.send("feature_events", event)  # Producer already has value_serializer
        kafka_producer.flush()
        
        # 4. Aguardar processamento
        time.sleep(10)  # Dar mais tempo para o processamento
        
        # 5. Consultar valores
        response = await client.get(f"/api/v1/features/{feature['id']}/values/test_entity/")
        assert response.status_code == 200
        values = response.json()
        assert len(values) > 0
        assert values[0]["value"] == 42.0

@pytest.mark.asyncio
async def test_feature_monitoring():
    """
    Teste end-to-end do monitoramento:
    1. Verificar health check
    2. Verificar métricas
    """
    async with AsyncClient(base_url="http://backend:8000", follow_redirects=True) as client:
        # 1. Health Check
        response = await client.get("/api/v1/monitoring/health/")
        assert response.status_code == 200
        health_data = response.json()
        assert health_data["overall"] == "healthy"
        
        # 2. Métricas
        response = await client.get("/api/v1/monitoring/metrics/")
        assert response.status_code == 200
        metrics_data = response.json()
        assert "total_feature_groups" in metrics_data
        assert "total_features" in metrics_data
        assert metrics_data["total_feature_groups"] >= 1  # Should have at least our test group
        assert metrics_data["total_features"] >= 1  # Should have at least our test feature
