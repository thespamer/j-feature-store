import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/monitoring/health")
        assert response.status_code == 200
        data = response.json()
        assert "mongodb" in data
        assert "redis" in data
        assert "overall" in data
        assert "timestamp" in data
        assert data["mongodb"] in ["healthy", "unhealthy"]
        assert data["redis"] in ["healthy", "unhealthy"]
        assert data["overall"] in ["healthy", "unhealthy"]

@pytest.mark.asyncio
async def test_metrics():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/monitoring/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "total_features" in data
        assert "total_feature_groups" in data
        assert "connections" in data
        assert "timestamp" in data
        assert isinstance(data["total_features"], int)
        assert isinstance(data["total_feature_groups"], int)
        assert "mongodb" in data["connections"]
        assert "redis" in data["connections"]
        assert "overall" in data["connections"]
        assert data["connections"]["mongodb"] in ["healthy", "unhealthy"]
        assert data["connections"]["redis"] in ["healthy", "unhealthy"]
        assert data["connections"]["overall"] in ["healthy", "unhealthy"]
