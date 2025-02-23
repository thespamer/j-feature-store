from abc import ABC, abstractmethod
from typing import Any, Dict, List
import pandas as pd

class FeatureTransformer(ABC):
    """Base class for all feature transformers."""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        
    @abstractmethod
    async def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Transform the input data."""
        pass
    
    @abstractmethod
    async def fit(self, data: pd.DataFrame) -> None:
        """Fit the transformer on training data."""
        pass
    
    def get_config(self) -> Dict[str, Any]:
        """Get transformer configuration."""
        return {
            "name": self.name,
            "type": self.__class__.__name__,
            "config": self.config
        }
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'FeatureTransformer':
        """Create transformer from configuration."""
        return cls(name=config["name"], config=config.get("config", {}))
