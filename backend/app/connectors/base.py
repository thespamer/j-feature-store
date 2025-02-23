from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class ConnectorConfig(BaseModel):
    type: str
    name: str
    config: Dict[str, Any] = {}

class BaseConnector(ABC):
    def __init__(self, config: ConnectorConfig):
        self.config = config
        self.validate_config()
        self.initialize()

    @abstractmethod
    def validate_config(self) -> None:
        """Validate the connector configuration"""
        pass

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the connector"""
        pass

    @abstractmethod
    def read_feature(self, feature_name: str, entity_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Read feature values"""
        pass

    @abstractmethod
    def write_feature(self, feature_name: str, values: Dict[str, Any]) -> None:
        """Write feature values"""
        pass

    @abstractmethod
    def list_features(self) -> List[str]:
        """List available features"""
        pass

    def close(self) -> None:
        """Close any open connections"""
        pass
