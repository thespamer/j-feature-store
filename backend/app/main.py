from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import features, feature_groups, monitoring
from app.core.store import initialize_store

app = FastAPI(title="Feature Store API")

# Configurar CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://frontend:3000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

@app.on_event("startup")
async def startup():
    await initialize_store()

# Incluir routers
app.include_router(features.router, prefix="/api/v1/features", tags=["features"])
app.include_router(feature_groups.router, prefix="/api/v1/feature-groups", tags=["feature-groups"])
app.include_router(monitoring.router, prefix="/api/v1/monitoring", tags=["monitoring"])

@app.get("/")
async def root():
    return {"message": "Feature Store API"}
