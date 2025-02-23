from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class FeatureVersion(BaseModel):
    version: str
    created_at: Optional[datetime] = None
    transformer_config: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
