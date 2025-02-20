from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class FeatureValue(BaseModel):
    value: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
class Feature(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    data_type: str = "float"  # float, int, string, etc.
    entity_id: str
    feature_group_id: str
    tags: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = {}
    
class FeatureGroup(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    entity_type: str  # user, product, transaction, etc.
    features: List[str] = []  # list of feature names
    tags: List[str] = []
    frequency: Optional[str] = None  # daily, hourly, real-time
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = {}
