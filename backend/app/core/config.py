"""Configuration settings for the Feature Store."""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings."""
    
    # MongoDB
    MONGODB_URL: str = "mongodb://mongodb:27017"
    MONGODB_DB: str = "feature_store"
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    
    # Postgres
    POSTGRES_URL: str = "postgresql://postgres:postgres@postgres:5432/feature_store"
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Feature Store"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Security
    SECRET_KEY: str = "your-super-secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["*"]
    
    # Performance
    CACHE_TTL: int = 300  # 5 minutes
    MAX_CONNECTIONS: int = 10
    
    class Config:
        """Model configuration."""
        case_sensitive = True

settings = Settings()
