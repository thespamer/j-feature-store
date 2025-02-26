from typing import Optional, List
import pandas as pd
import numpy as np
from datetime import datetime

from .base import BaseTransformation

class TemporalTransformation(BaseTransformation):
    def extract_components(self, data: pd.Series) -> pd.DataFrame:
        """Extrai componentes temporais (ano, mês, dia, etc.)"""
        components = pd.DataFrame(index=data.index)
        components['year'] = data.dt.year
        components['month'] = data.dt.month
        components['day'] = data.dt.day
        components['dayofweek'] = data.dt.dayofweek
        components['hour'] = data.dt.hour
        components['minute'] = data.dt.minute
        components['second'] = data.dt.second
        components['quarter'] = data.dt.quarter
        components['is_weekend'] = data.dt.dayofweek.isin([5, 6]).astype(int)
        return components

    def to_unix_timestamp(self, data: pd.Series) -> pd.Series:
        """Converte para timestamp Unix"""
        return data.astype(np.int64) // 10**9

    def cyclical_encode(self, data: pd.Series, feature: str) -> pd.DataFrame:
        """Codifica características cíclicas (mês, dia da semana, etc.)"""
        max_vals = {
            'month': 12,
            'day': 31,
            'dayofweek': 7,
            'hour': 24,
            'minute': 60,
            'second': 60
        }
        
        if feature not in max_vals:
            raise ValueError(f"Feature {feature} não suportada para codificação cíclica")
            
        max_val = max_vals[feature]
        values = getattr(data.dt, feature)
        
        df = pd.DataFrame(index=data.index)
        df[f'{feature}_sin'] = np.sin(2 * np.pi * values / max_val)
        df[f'{feature}_cos'] = np.cos(2 * np.pi * values / max_val)
        return df

    def time_since_reference(self, data: pd.Series, reference_date: datetime) -> pd.Series:
        """Calcula tempo desde uma data de referência em dias"""
        return (data - pd.Timestamp(reference_date)).dt.total_seconds() / (24 * 60 * 60)

    def time_difference(self, data: pd.Series, shift: int = 1) -> pd.Series:
        """Calcula diferença de tempo entre registros consecutivos"""
        return data.diff(shift).dt.total_seconds()

    def create_time_windows(self, data: pd.Series, window_size: str = '1D') -> pd.Series:
        """Cria janelas de tempo"""
        return pd.Series(data.dt.floor(window_size), index=data.index)

    def handle_missing(self, data: pd.Series, strategy: str = 'forward_fill') -> pd.Series:
        """Trata valores faltantes em séries temporais"""
        if strategy == 'forward_fill':
            return data.ffill()
        elif strategy == 'backward_fill':
            return data.bfill()
        elif strategy == 'interpolate':
            return data.interpolate(method='time')
        else:
            raise ValueError(f"Estratégia {strategy} não suportada")
