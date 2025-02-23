from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class FeatureGroup(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    entity_id: str
    tags: List[str] = []
    frequency: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    features: List[str] = []
    entity_type: str

class Feature(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    feature_group_id: str
    type: str
    entity_id: str
    tags: List[str] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class FeatureValue(BaseModel):
    feature_id: str
    entity_id: str
    value: str
    timestamp: Optional[datetime] = None

class FeatureCreate(BaseModel):
    name: str
    description: str
    feature_group_id: str
    type: str
    entity_id: str
    tags: List[str] = []
