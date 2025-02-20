from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import features, feature_groups, monitoring

app = FastAPI(title="Feature Store API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(features.router, prefix="/api/v1/features", tags=["features"])
app.include_router(feature_groups.router, prefix="/api/v1/feature-groups", tags=["feature_groups"])
app.include_router(monitoring.router, prefix="/api/v1/monitoring", tags=["monitoring"])

@app.get("/")
async def root():
    return {"message": "Feature Store API"}
