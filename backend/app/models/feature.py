from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class FeatureType(str, Enum):
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    TEMPORAL = "temporal"
    TEXT = "text"

class FeatureValueType(str, Enum):
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"

class Feature(BaseModel):
    name: str
    description: Optional[str]
    feature_type: FeatureType
    value_type: FeatureValueType
    entity: str
    tags: List[str] = []
    owners: List[str] = []
    created_at: datetime
    updated_at: datetime
    version: str
    batch_source: Optional[Dict[str, Any]]
    stream_source: Optional[Dict[str, Any]]
    transformation_logic: Optional[str]
    validation_rules: Optional[Dict[str, Any]]
    metadata: Dict[str, Any] = {}

class FeatureValue(BaseModel):
    feature_name: str
    entity_key: str
    value: Any
    timestamp: datetime

class FeatureGroup(BaseModel):
    name: str
    description: Optional[str]
    features: List[Feature]
    entity: str
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime
    version: str
    metadata: Dict[str, Any] = {}
