import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.feature import Feature, FeatureSource
from datetime import datetime

client = TestClient(app)

@pytest.fixture
def sample_feature():
    return {
        "name": "customer_lifetime_value",
        "description": "Total value of customer purchases",
        "source": {
            "type": "postgresql",
            "query": "SELECT customer_id, SUM(value) FROM orders GROUP BY customer_id",
            "update_frequency": "1h"
        },
        "tags": ["customer", "financial"],
        "owner": "data_team"
    }

def test_create_feature(sample_feature):
    response = client.post("/api/v1/features/", json=sample_feature)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == sample_feature["name"]
    assert "id" in data

def test_get_feature():
    # First create a feature
    feature_data = {
        "name": "test_feature",
        "description": "Test feature",
        "source": {
            "type": "mongodb",
            "collection": "test",
            "query": {"field": "value"}
        }
    }
    create_response = client.post("/api/v1/features/", json=feature_data)
    feature_id = create_response.json()["id"]

    # Then get it
    response = client.get(f"/api/v1/features/{feature_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == feature_data["name"]

def test_list_features():
    response = client.get("/api/v1/features/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_update_feature(sample_feature):
    # First create a feature
    create_response = client.post("/api/v1/features/", json=sample_feature)
    feature_id = create_response.json()["id"]

    # Update it
    update_data = {
        "description": "Updated description"
    }
    response = client.patch(f"/api/v1/features/{feature_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["description"] == update_data["description"]

def test_delete_feature(sample_feature):
    # First create a feature
    create_response = client.post("/api/v1/features/", json=sample_feature)
    feature_id = create_response.json()["id"]

    # Delete it
    response = client.delete(f"/api/v1/features/{feature_id}")
    assert response.status_code == 204

    # Verify it's gone
    get_response = client.get(f"/api/v1/features/{feature_id}")
    assert get_response.status_code == 404
