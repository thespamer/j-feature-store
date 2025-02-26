"""Fixtures compartilhadas para testes."""
import os
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from datetime import datetime

import pandas as pd
import numpy as np
from motor.motor_asyncio import AsyncIOMotorClient
from redis import Redis
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.transformations.numeric import NumericTransformation
from app.transformations.categorical import CategoricalTransformation
from app.transformations.temporal import TemporalTransformation

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Cria um event loop para testes assíncronos."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_app():
    """Retorna uma instância do aplicativo FastAPI para testes."""
    return app

@pytest.fixture(scope="session")
def client(test_app):
    """Retorna um cliente de teste para o FastAPI."""
    return TestClient(test_app)

@pytest.fixture(scope="session")
async def mongodb_client() -> AsyncGenerator[AsyncIOMotorClient, None]:
    """Retorna um cliente MongoDB para testes."""
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    yield client
    await client.close()

@pytest.fixture(scope="session")
def redis_client():
    """Retorna um cliente Redis para testes."""
    client = Redis.from_url(settings.REDIS_URL)
    yield client
    client.close()

@pytest.fixture
def sample_numeric_data():
    """Gera dados numéricos de exemplo."""
    np.random.seed(42)
    return pd.Series(np.random.normal(100, 15, 1000))

@pytest.fixture
def sample_categorical_data():
    """Gera dados categóricos de exemplo."""
    categories = ['A', 'B', 'C', 'D']
    return pd.Series(np.random.choice(categories, 1000))

@pytest.fixture
def sample_temporal_data():
    """Gera dados temporais de exemplo."""
    dates = pd.date_range(start='2025-01-01', periods=1000, freq='H')
    return pd.Series(dates)

@pytest.fixture
def numeric_transformer():
    """Retorna uma instância de NumericTransformation."""
    return NumericTransformation()

@pytest.fixture
def categorical_transformer():
    """Retorna uma instância de CategoricalTransformation."""
    return CategoricalTransformation()

@pytest.fixture
def temporal_transformer():
    """Retorna uma instância de TemporalTransformation."""
    return TemporalTransformation()

@pytest.fixture
def sample_feature_definition():
    """Retorna uma definição de feature de exemplo."""
    return {
        "name": "test_feature",
        "description": "Feature para testes",
        "type": "numeric",
        "metadata": {
            "owner": "test_team",
            "created_at": datetime.utcnow().isoformat(),
            "tags": ["test", "example"]
        },
        "validation_rules": {
            "min_value": 0,
            "max_value": 1000
        },
        "transformation": {
            "type": "standard_scaler",
            "params": {}
        }
    }

@pytest.fixture(autouse=True)
async def cleanup_collections(mongodb_client):
    """Limpa as coleções do MongoDB após cada teste."""
    yield
    db = mongodb_client.get_database('feature_store')
    collections = await db.list_collection_names()
    for collection in collections:
        await db[collection].delete_many({})

@pytest.fixture(autouse=True)
def cleanup_redis(redis_client):
    """Limpa o Redis após cada teste."""
    yield
    redis_client.flushall()
