from pydantic import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "FStore"
    API_V1_STR: str = "/api"
    
    # Database URIs
    MONGODB_URI: str
    REDIS_URI: str
    POSTGRES_URI: str
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # Security
    SECRET_KEY: str = "your-secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    class Config:
        case_sensitive = True

settings = Settings()
