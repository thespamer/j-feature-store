from app.services.feature_store import FeatureStore
from app.db.mongodb import get_database
import asyncpg
from app.core.config import settings

# Criar uma única instância do FeatureStore
feature_store = None

# Função para obter a instância do FeatureStore
def get_feature_store():
    global feature_store
    return feature_store

# Função para inicializar o FeatureStore
async def initialize_store():
    global feature_store
    if feature_store is None:
        mongodb_client = await get_database()
        postgres_pool = await asyncpg.create_pool(
            settings.POSTGRES_URL,
            min_size=5,
            max_size=10
        )
        feature_store = FeatureStore(mongodb_client, postgres_pool)
        await feature_store.initialize()
