from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import monitoring, features

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
app.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])
app.include_router(features.router, prefix="/api/v1", tags=["features"])

@app.get("/")
async def root():
    return {"message": "Welcome to FStore API"}
