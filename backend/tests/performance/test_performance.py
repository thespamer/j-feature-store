import pytest
import asyncio
import time
from typing import List, Dict, Any
from datetime import datetime, timedelta

import numpy as np
from fastapi.testclient import TestClient

from app.main import app
from app.models.feature import Feature, FeatureValue
from app.db.mongodb import get_database

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def large_feature_data() -> List[Dict[str, Any]]:
    """Gera um grande conjunto de dados de features para teste"""
    features = []
    for i in range(1000):
        features.append({
            "name": f"feature_{i}",
            "description": f"Feature de teste {i}",
            "type": "numeric",
            "metadata": {
                "owner": "performance_test",
                "tags": ["test", "performance"]
            }
        })
    return features

@pytest.fixture
def large_value_data() -> List[Dict[str, Any]]:
    """Gera um grande conjunto de valores para teste"""
    values = []
    base_time = datetime.utcnow()
    for i in range(1000):
        values.append({
            "value": np.random.random() * 100,
            "timestamp": (base_time - timedelta(minutes=i)).isoformat(),
            "metadata": {
                "source": "performance_test",
                "batch_id": i // 100
            }
        })
    return values

@pytest.mark.benchmark
class TestFeatureCreationPerformance:
    def test_bulk_feature_creation(self, test_client, large_feature_data, benchmark):
        """Testa a performance da criação em massa de features"""
        def create_features():
            responses = []
            for feature in large_feature_data:
                response = test_client.post("/api/v1/features", json=feature)
                responses.append(response)
            return responses

        results = benchmark(create_features)
        
        # Verifica se todas as criações foram bem-sucedidas
        assert all(r.status_code == 201 for r in results)
        
        # Verifica o tempo médio por feature
        avg_time = benchmark.stats.stats.mean
        assert avg_time < 0.1  # menos de 100ms por feature

    def test_parallel_feature_creation(self, test_client, large_feature_data):
        """Testa a criação paralela de features"""
        async def create_feature(feature):
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None,
                lambda: test_client.post("/api/v1/features", json=feature)
            )

        async def create_all():
            tasks = [create_feature(f) for f in large_feature_data[:100]]
            start_time = time.time()
            responses = await asyncio.gather(*tasks)
            end_time = time.time()
            return responses, end_time - start_time

        responses, total_time = asyncio.run(create_all())
        
        # Verifica se todas as criações foram bem-sucedidas
        assert all(r.status_code == 201 for r in responses)
        
        # Verifica se o tempo total é aceitável (menos de 5s para 100 features)
        assert total_time < 5.0

@pytest.mark.benchmark
class TestFeatureValuePerformance:
    def test_bulk_value_insertion(self, test_client, large_value_data, benchmark):
        """Testa a inserção em massa de valores"""
        # Primeiro cria uma feature para teste
        feature_response = test_client.post("/api/v1/features", json={
            "name": "performance_test_feature",
            "type": "numeric"
        })
        feature_id = feature_response.json()["id"]

        def insert_values():
            responses = []
            for value in large_value_data:
                response = test_client.post(
                    f"/api/v1/features/{feature_id}/values",
                    json=value
                )
                responses.append(response)
            return responses

        results = benchmark(insert_values)
        
        # Verifica se todas as inserções foram bem-sucedidas
        assert all(r.status_code == 201 for r in results)
        
        # Verifica o tempo médio por inserção
        avg_time = benchmark.stats.stats.mean
        assert avg_time < 0.05  # menos de 50ms por valor

    def test_value_query_performance(self, test_client, large_value_data, benchmark):
        """Testa a performance das consultas de valores"""
        # Primeiro cria uma feature e insere valores
        feature_response = test_client.post("/api/v1/features", json={
            "name": "query_test_feature",
            "type": "numeric"
        })
        feature_id = feature_response.json()["id"]

        # Insere alguns valores
        for value in large_value_data[:100]:
            test_client.post(
                f"/api/v1/features/{feature_id}/values",
                json=value
            )

        def query_values():
            return test_client.get(
                f"/api/v1/features/{feature_id}/values",
                params={"limit": 100}
            )

        result = benchmark(query_values)
        
        # Verifica se a consulta foi bem-sucedida
        assert result.status_code == 200
        
        # Verifica o tempo de resposta
        avg_time = benchmark.stats.stats.mean
        assert avg_time < 0.1  # menos de 100ms para consultar 100 valores

@pytest.mark.benchmark
class TestCachePerformance:
    def test_cache_hit_performance(self, test_client, benchmark):
        """Testa a performance do cache"""
        # Cria uma feature para teste
        feature_response = test_client.post("/api/v1/features", json={
            "name": "cache_test_feature",
            "type": "numeric"
        })
        feature_id = feature_response.json()["id"]

        def get_feature():
            return test_client.get(f"/api/v1/features/{feature_id}")

        # Primeira chamada (cache miss)
        first_call = get_feature()
        assert first_call.status_code == 200

        # Benchmark das chamadas subsequentes (cache hit)
        result = benchmark(get_feature)
        
        # Verifica se todas as chamadas foram bem-sucedidas
        assert result.status_code == 200
        
        # Verifica o tempo de resposta do cache
        avg_time = benchmark.stats.stats.mean
        assert avg_time < 0.01  # menos de 10ms para cache hit

@pytest.mark.benchmark
class TestDatabasePerformance:
    def test_database_query_performance(self, test_client, benchmark):
        """Testa a performance das queries no banco de dados"""
        # Cria várias features para teste
        for i in range(100):
            test_client.post("/api/v1/features", json={
                "name": f"db_test_feature_{i}",
                "type": "numeric"
            })

        def search_features():
            return test_client.get("/api/v1/features", params={
                "search": "test",
                "limit": 50
            })

        result = benchmark(search_features)
        
        # Verifica se a busca foi bem-sucedida
        assert result.status_code == 200
        
        # Verifica o tempo de resposta
        avg_time = benchmark.stats.stats.mean
        assert avg_time < 0.2  # menos de 200ms para buscar 50 features
