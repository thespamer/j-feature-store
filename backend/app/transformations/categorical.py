from typing import Any, Dict, List
import pandas as pd
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from .base import FeatureTransformer

class CategoricalTransformer(FeatureTransformer):
    """Transformer for categorical features with encoding options."""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.method = self.config.get("method", "label")
        self._encoder = None
        
        if self.method == "label":
            self._encoder = LabelEncoder()
        elif self.method == "onehot":
            self._encoder = OneHotEncoder(sparse=False)
        else:
            raise ValueError(f"Unknown encoding method: {self.method}")
    
    async def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Transform categorical data using the fitted encoder."""
        if self._encoder is None:
            raise ValueError("Transformer not fitted")
            
        if self.method == "label":
            return pd.DataFrame(
                self._encoder.transform(data),
                columns=data.columns,
                index=data.index
            )
        else:  # onehot
            transformed = self._encoder.transform(data)
            return pd.DataFrame(
                transformed,
                columns=self._encoder.get_feature_names_out(data.columns),
                index=data.index
            )
    
    async def fit(self, data: pd.DataFrame) -> None:
        """Fit the encoder on training data."""
        if self.method == "label":
            self._encoder.fit(data.values.ravel())
        else:  # onehot
            self._encoder.fit(data)
            
    def get_config(self) -> Dict[str, Any]:
        """Get transformer configuration including fitted parameters."""
        config = super().get_config()
        if self.method == "label":
            config["fitted_params"] = {
                "classes": self._encoder.classes_.tolist()
            }
        elif self.method == "onehot":
            config["fitted_params"] = {
                "categories": [cat.tolist() for cat in self._encoder.categories_],
                "feature_names": self._encoder.get_feature_names_out().tolist()
            }
        return config
