from pydantic import BaseModel, Field
from typing import List, Optional

class FeatureGroup(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: str = Field(...)
    description: str = Field(default="")
    entity_id: str = Field(default="")
    tags: List[str] = Field(default_factory=list)

    class Config:
        populate_by_name = True
        json_encoders = {
            str: str
        }
