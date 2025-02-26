from typing import Any, Dict, List, Optional
import pandas as pd
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
import numpy as np

from .base import BaseTransformation

class CategoricalTransformation(BaseTransformation):
    """Transformer for categorical features with encoding options."""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.method = self.config.get("method", "label")
        self._encoder = None
        self.handle_missing_strategy = self.config.get("handle_missing_strategy", "mode")
        self.group_rare_categories_min_freq = self.config.get("group_rare_categories_min_freq", 0.01)
        
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
            
        data = data.apply(self.handle_missing, strategy=self.handle_missing_strategy)
        data = data.apply(self.group_rare_categories, min_freq=self.group_rare_categories_min_freq)
        
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
        data = data.apply(self.handle_missing, strategy=self.handle_missing_strategy)
        data = data.apply(self.group_rare_categories, min_freq=self.group_rare_categories_min_freq)
        
        if self.method == "label":
            self._encoder.fit(data.values.ravel())
        else:  # onehot
            self._encoder.fit(data)
            
    def handle_missing(self, data: pd.Series, strategy: str = 'mode') -> pd.Series:
        """Trata valores faltantes"""
        if strategy == 'mode':
            return data.fillna(data.mode()[0])
        elif strategy == 'new_category':
            return data.fillna('MISSING')
        elif strategy == 'most_frequent':
            return data.fillna(data.value_counts().index[0])
        else:
            raise ValueError(f"Estratégia {strategy} não suportada")

    def group_rare_categories(self, data: pd.Series, min_freq: float = 0.01) -> pd.Series:
        """Agrupa categorias raras em uma única categoria"""
        value_counts = data.value_counts(normalize=True)
        rare_categories = value_counts[value_counts < min_freq].index
        return data.replace(rare_categories, 'RARE')

    def one_hot_encode(self, data: pd.Series) -> pd.DataFrame:
        """Aplica one-hot encoding"""
        encoder = OneHotEncoder(sparse=False, handle_unknown='ignore')
        reshaped_data = data.values.reshape(-1, 1)
        encoded = encoder.fit_transform(reshaped_data)
        
        # Criar DataFrame com nomes de colunas apropriados
        categories = encoder.categories_[0]
        column_names = [f"{data.name}_{cat}" for cat in categories]
        return pd.DataFrame(encoded, columns=column_names, index=data.index)

    def label_encode(self, data: pd.Series) -> pd.Series:
        """Aplica label encoding"""
        encoder = LabelEncoder()
        return pd.Series(encoder.fit_transform(data), index=data.index)

    def frequency_encode(self, data: pd.Series) -> pd.Series:
        """Codifica categorias pela sua frequência"""
        freq = data.value_counts(normalize=True)
        return data.map(freq)

    def target_encode(self, data: pd.Series, target: pd.Series, smoothing: float = 10) -> pd.Series:
        """Aplica target encoding com smoothing"""
        global_mean = target.mean()
        agg = pd.DataFrame({'target': target, 'feature': data}).groupby('feature')
        counts = agg.size()
        means = agg['target'].mean()
        
        # Aplicar smoothing
        smooth = (counts * means + smoothing * global_mean) / (counts + smoothing)
        return data.map(smooth)

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
        config["handle_missing_strategy"] = self.handle_missing_strategy
        config["group_rare_categories_min_freq"] = self.group_rare_categories_min_freq
        return config
