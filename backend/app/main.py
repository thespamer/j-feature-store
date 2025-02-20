from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .routers import features, registry, monitoring
from .core.config import settings

app = FastAPI(title="FStore API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(features.router, prefix="/api/features", tags=["features"])
app.include_router(registry.router, prefix="/api/registry", tags=["registry"])
app.include_router(monitoring.router, prefix="/api/monitoring", tags=["monitoring"])

@app.get("/")
async def root():
    return {"message": "Welcome to FStore API"}
