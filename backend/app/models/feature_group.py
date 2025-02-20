from pydantic import BaseModel
from typing import List
from datetime import datetime

class FeatureGroup(BaseModel):
    id: str
    name: str
    description: str
    entity_type: str
    frequency: str
    tags: List[str]
    created_at: datetime
