from app.services.feature_store import FeatureStore

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
        feature_store = FeatureStore()
        await feature_store.initialize()
