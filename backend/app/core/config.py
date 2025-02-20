from pydantic import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "FStore"
    API_V1_STR: str = "/api"
    
    # Database URIs
    MONGODB_URI: str = "mongodb://mongodb:27017/fstore"
    REDIS_URI: str = "redis://redis:6380/0"
    POSTGRES_URI: str = "postgresql://postgres:postgres@postgres:5432/fstore"
    
    # Kafka (optional)
    KAFKA_BOOTSTRAP_SERVERS: Optional[str] = None
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # Security
    SECRET_KEY: str = "your-secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    class Config:
        case_sensitive = True

settings = Settings()
