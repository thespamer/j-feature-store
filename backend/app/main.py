from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import features, feature_groups, monitoring
from app.core.store import initialize_store
from app.services.feature_store import FeatureStore
from app.db import get_db

app = FastAPI(title="Feature Store API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(features.router, prefix="/api/v1", tags=["features"])
app.include_router(feature_groups.router, prefix="/api/v1", tags=["feature-groups"])
app.include_router(monitoring.router, prefix="/api/v1", tags=["monitoring"])

@app.on_event("startup")
async def startup_event():
    await initialize_store()
    # db = await get_db() - Removido pois FeatureStore não precisa deste parâmetro
    # app.state.feature_store = FeatureStore(db) - Inicialização já feita em initialize_store()

@app.get("/")
async def root():
    return {"message": "Feature Store API"}

@app.get("/features")
async def list_features():
    feature_store = get_feature_store()
    return await feature_store.list_features()

@app.get("/test-mongo")
async def test_mongo():
    """Testa a conexão com o MongoDB."""
    try:
        feature_store = get_feature_store()
        if not feature_store:
            return {"status": "error", "message": "FeatureStore não inicializado"}
        
        # Tenta listar as coleções para verificar a conexão
        collections = await feature_store.db.list_collection_names()
        return {
            "status": "success",
            "message": "Conexão com MongoDB estabelecida com sucesso",
            "collections": collections,
            "database": settings.MONGODB_DB
        }
    except Exception as e:
        return {"status": "error", "message": f"Erro ao conectar com MongoDB: {str(e)}"}
