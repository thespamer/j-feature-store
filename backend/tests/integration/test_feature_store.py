import pytest
from datetime import datetime, timedelta
from typing import Dict, Any

from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient

from app.main import app
from app.core.config import settings
from app.models.feature import Feature, FeatureValue
from app.db.mongodb import get_database

@pytest.fixture
async def test_db():
    """Fixture para criar e limpar o banco de teste"""
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client.get_database("test_db")
    yield db
    await client.drop_database("test_db")
    client.close()

@pytest.fixture
def test_client(test_db):
    """Fixture para criar um cliente de teste"""
    app.dependency_overrides[get_database] = lambda: test_db
    return TestClient(app)

@pytest.fixture
def feature_data() -> Dict[str, Any]:
    """Fixture com dados de exemplo de uma feature"""
    return {
        "name": "test_feature",
        "description": "Feature para teste de integração",
        "type": "numeric",
        "metadata": {
            "owner": "test_team",
            "tags": ["test", "integration"]
        }
    }

@pytest.fixture
def feature_value_data() -> Dict[str, Any]:
    """Fixture com dados de exemplo de um valor de feature"""
    return {
        "value": 42.0,
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": {
            "source": "integration_test",
            "confidence": 0.99
        }
    }

@pytest.mark.asyncio
class TestFeatureStoreAPI:
    async def test_create_feature(self, test_client, feature_data):
        """Testa a criação de uma feature via API"""
        response = test_client.post("/api/v1/features", json=feature_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == feature_data["name"]
        assert "id" in data

    async def test_get_feature(self, test_client, feature_data):
        """Testa a recuperação de uma feature via API"""
        # Primeiro cria a feature
        create_response = test_client.post("/api/v1/features", json=feature_data)
        feature_id = create_response.json()["id"]

        # Depois recupera
        response = test_client.get(f"/api/v1/features/{feature_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == feature_data["name"]

    async def test_update_feature(self, test_client, feature_data):
        """Testa a atualização de uma feature via API"""
        # Cria a feature
        create_response = test_client.post("/api/v1/features", json=feature_data)
        feature_id = create_response.json()["id"]

        # Atualiza a feature
        update_data = {"description": "Descrição atualizada"}
        response = test_client.put(f"/api/v1/features/{feature_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == update_data["description"]

    async def test_delete_feature(self, test_client, feature_data):
        """Testa a deleção de uma feature via API"""
        # Cria a feature
        create_response = test_client.post("/api/v1/features", json=feature_data)
        feature_id = create_response.json()["id"]

        # Deleta a feature
        response = test_client.delete(f"/api/v1/features/{feature_id}")
        assert response.status_code == 204

        # Verifica se foi realmente deletada
        get_response = test_client.get(f"/api/v1/features/{feature_id}")
        assert get_response.status_code == 404

    async def test_create_feature_value(self, test_client, feature_data, feature_value_data):
        """Testa a criação de um valor de feature via API"""
        # Cria a feature
        create_response = test_client.post("/api/v1/features", json=feature_data)
        feature_id = create_response.json()["id"]

        # Cria o valor
        response = test_client.post(
            f"/api/v1/features/{feature_id}/values",
            json=feature_value_data
        )
        assert response.status_code == 201
        data = response.json()
        assert data["value"] == feature_value_data["value"]

    async def test_get_feature_values(self, test_client, feature_data, feature_value_data):
        """Testa a recuperação de valores de feature via API"""
        # Cria a feature
        create_response = test_client.post("/api/v1/features", json=feature_data)
        feature_id = create_response.json()["id"]

        # Cria múltiplos valores
        for i in range(3):
            value_data = feature_value_data.copy()
            value_data["value"] = i
            value_data["timestamp"] = (
                datetime.utcnow() - timedelta(hours=i)
            ).isoformat()
            test_client.post(
                f"/api/v1/features/{feature_id}/values",
                json=value_data
            )

        # Recupera os valores
        response = test_client.get(f"/api/v1/features/{feature_id}/values")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        # Verifica se estão ordenados por timestamp
        timestamps = [datetime.fromisoformat(v["timestamp"]) for v in data]
        assert timestamps == sorted(timestamps, reverse=True)

    async def test_feature_value_validation(self, test_client, feature_data):
        """Testa a validação de valores de feature via API"""
        # Cria a feature
        create_response = test_client.post("/api/v1/features", json=feature_data)
        feature_id = create_response.json()["id"]

        # Tenta criar um valor inválido
        invalid_value = {
            "value": "not_a_number",  # deveria ser numérico
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {}
        }
        response = test_client.post(
            f"/api/v1/features/{feature_id}/values",
            json=invalid_value
        )
        assert response.status_code == 422  # Unprocessable Entity
