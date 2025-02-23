from typing import Any, Dict, List
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from .base import FeatureTransformer

class NumericTransformer(FeatureTransformer):
    """Transformer for numeric features with scaling options."""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.method = self.config.get("method", "standard")
        self._scaler = None
        
        if self.method == "standard":
            self._scaler = StandardScaler()
        elif self.method == "minmax":
            self._scaler = MinMaxScaler()
        else:
            raise ValueError(f"Unknown scaling method: {self.method}")
    
    async def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Transform numeric data using the fitted scaler."""
        if self._scaler is None:
            raise ValueError("Transformer not fitted")
        
        return pd.DataFrame(
            self._scaler.transform(data),
            columns=data.columns,
            index=data.index
        )
    
    async def fit(self, data: pd.DataFrame) -> None:
        """Fit the scaler on training data."""
        self._scaler.fit(data)
        
    def get_config(self) -> Dict[str, Any]:
        """Get transformer configuration including fitted parameters."""
        config = super().get_config()
        if hasattr(self._scaler, "mean_") and hasattr(self._scaler, "scale_"):
            config["fitted_params"] = {
                "mean": self._scaler.mean_.tolist(),
                "scale": self._scaler.scale_.tolist()
            }
        return config
