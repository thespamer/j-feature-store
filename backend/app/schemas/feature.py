from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class FeatureBase(BaseModel):
    name: str = Field(..., description="Nome da feature")
    description: Optional[str] = Field(None, description="Descrição da feature")
    type: str = Field(..., description="Tipo da feature (numeric, categorical, temporal)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados adicionais")

class FeatureCreate(FeatureBase):
    validation_rules: Optional[Dict[str, Any]] = Field(None, description="Regras de validação")
    transformation: Optional[Dict[str, Any]] = Field(None, description="Configuração de transformação")

class FeatureUpdate(BaseModel):
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    validation_rules: Optional[Dict[str, Any]] = None
    transformation: Optional[Dict[str, Any]] = None

class FeatureValue(BaseModel):
    value: Any
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Feature(FeatureBase):
    id: str
    created_at: datetime
    updated_at: datetime
    version: str
    status: str = "active"

    class Config:
        from_attributes = True
