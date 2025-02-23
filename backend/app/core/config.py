from pydantic import BaseModel
from typing import Optional

class Settings(BaseModel):
    PROJECT_NAME: str = "Feature Store API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    MONGODB_URL: str = "mongodb://mongodb:27017"
    MONGODB_DB: str = "fstore"
    
    REDIS_URL: str = "redis://redis:6379/0"
    
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:9092"
    KAFKA_TOPIC_PREFIX: str = "feature_store"
    
    POSTGRES_SERVER: str = "postgres"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "fstore"

settings = Settings()
