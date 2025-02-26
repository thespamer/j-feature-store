from typing import Optional
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler

from .base import BaseTransformation

class NumericTransformation(BaseTransformation):
    def standardize(self, data: pd.Series) -> pd.Series:
        """Padroniza os dados usando StandardScaler"""
        scaler = StandardScaler()
        reshaped_data = data.values.reshape(-1, 1)
        return pd.Series(scaler.fit_transform(reshaped_data).flatten(), index=data.index)

    def normalize(self, data: pd.Series) -> pd.Series:
        """Normaliza os dados para o intervalo [0,1]"""
        scaler = MinMaxScaler()
        reshaped_data = data.values.reshape(-1, 1)
        return pd.Series(scaler.fit_transform(reshaped_data).flatten(), index=data.index)

    def log_transform(self, data: pd.Series) -> pd.Series:
        """Aplica transformação logarítmica"""
        return np.log1p(data)

    def handle_missing(self, data: pd.Series, strategy: str = 'mean') -> pd.Series:
        """Trata valores faltantes"""
        if strategy == 'mean':
            return data.fillna(data.mean())
        elif strategy == 'median':
            return data.fillna(data.median())
        elif strategy == 'mode':
            return data.fillna(data.mode()[0])
        elif strategy == 'zero':
            return data.fillna(0)
        else:
            raise ValueError(f"Estratégia {strategy} não suportada")

    def clip_outliers(self, data: pd.Series, lower: Optional[float] = None, upper: Optional[float] = None) -> pd.Series:
        """Remove outliers usando limites definidos ou IQR"""
        if lower is None or upper is None:
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
        return data.clip(lower=lower, upper=upper)
