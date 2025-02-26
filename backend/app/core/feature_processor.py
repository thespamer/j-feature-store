"""Módulo de processamento de features."""
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Any, Dict, Optional, Union

def handle_missing_values(data: pd.Series, strategy: str = "mean", fill_value: Optional[Any] = None) -> pd.Series:
    """Handle missing values in a pandas Series.
    
    Args:
        data: Input data series
        strategy: Strategy to handle missing values. One of:
            - mean: Fill with mean value (numeric only)
            - median: Fill with median value (numeric only)
            - mode: Fill with most frequent value
            - constant: Fill with a constant value
            - ffill: Forward fill
            - bfill: Backward fill
        fill_value: Value to use when strategy is 'constant'
    
    Returns:
        Series with missing values handled
    """
    if strategy == "mean":
        return data.fillna(data.mean())
    elif strategy == "median":
        return data.fillna(data.median())
    elif strategy == "mode":
        return data.fillna(data.mode()[0])
    elif strategy == "constant":
        return data.fillna(fill_value)
    elif strategy == "ffill":
        return data.fillna(method="ffill")
    elif strategy == "bfill":
        return data.fillna(method="bfill")
    else:
        raise ValueError(f"Invalid strategy: {strategy}")

def handle_outliers(data: pd.Series, method: str = "zscore", threshold: float = 3.0) -> pd.Series:
    """Handle outliers in a pandas Series.
    
    Args:
        data: Input data series
        method: Method to detect outliers. One of:
            - zscore: Use z-score method
            - iqr: Use interquartile range method
            - percentile: Use percentile method
        threshold: Threshold for outlier detection
            - For zscore: Number of standard deviations
            - For iqr: IQR multiplier
            - For percentile: Percentile value (0 to 1)
    
    Returns:
        Series with outliers handled
    """
    data = data.copy()
    if method == "zscore":
        # Calculate z-scores for each value
        mean = data.median()  # Use median instead of mean to be more robust
        mad = (data - mean).abs().median()  # Use MAD instead of std to be more robust
        z_scores = (data - mean).abs() / mad
        
        # Identify outliers
        outliers = z_scores > threshold
        
        # Replace outliers with mean ± threshold * std
        data.loc[outliers] = data.loc[outliers].apply(
            lambda x: mean + threshold * mad if x > mean else mean - threshold * mad
        )
    elif method == "iqr":
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        data = data.clip(lower=lower_bound, upper=upper_bound)
    elif method == "percentile":
        lower_bound = data.quantile(threshold)
        upper_bound = data.quantile(1 - threshold)
        data = data.clip(lower=lower_bound, upper=upper_bound)
    else:
        raise ValueError(f"Invalid method: {method}")
    return data

def process_numeric_feature(
    data: pd.Series,
    transformation: str,
    handle_nulls: Optional[str] = None,
    handle_outliers: bool = False
) -> pd.Series:
    """Processa feature numérica."""
    # Trata valores nulos
    if handle_nulls:
        if handle_nulls == "constant":
            data = handle_missing_values(data, strategy=handle_nulls, fill_value=0.0)
        else:
            data = handle_missing_values(data, strategy=handle_nulls)
    
    # Trata outliers
    if handle_outliers:
        from app.core.feature_processor import handle_outliers as handle_outliers_func
        data = handle_outliers_func(data, method="zscore", threshold=3.0)
    
    # Aplica transformação
    if transformation == "standard_scaler":
        return (data - data.mean()) / data.std()
    elif transformation == "min_max_scaler":
        return (data - data.min()) / (data.max() - data.min())
    elif transformation == "log_transform":
        return np.log1p(data)
    else:
        raise ValueError(f"Invalid transformation: {transformation}")

def process_categorical_feature(
    data: pd.Series,
    transformation: str,
    handle_nulls: Optional[str] = None,
    handle_rare: bool = False
) -> Union[pd.Series, pd.DataFrame]:
    """Processa feature categórica."""
    # Trata valores nulos
    if handle_nulls:
        data = handle_missing_values(data, strategy=handle_nulls, fill_value="MISSING")
    
    # Agrupa categorias raras
    if handle_rare:
        value_counts = data.value_counts(normalize=True)
        rare_categories = value_counts[value_counts < 0.05].index
        data = data.replace(rare_categories, "RARE")
    
    # Aplica transformação
    if transformation == "one_hot":
        return pd.get_dummies(data, prefix=data.name)
    elif transformation == "label_encoding":
        unique_values = data.unique()
        label_map = {val: idx for idx, val in enumerate(unique_values)}
        return data.map(label_map)
    else:
        raise ValueError(f"Invalid transformation: {transformation}")

def process_temporal_feature(
    data: pd.Series,
    transformation: str,
    handle_nulls: Optional[str] = None
) -> Union[pd.Series, pd.DataFrame]:
    """Processa feature temporal."""
    # Trata valores nulos
    if handle_nulls:
        data = handle_missing_values(data, strategy=handle_nulls)
    
    # Aplica transformação
    if transformation == "timestamp":
        return pd.to_numeric(data)
    elif transformation == "date_parts":
        result = pd.DataFrame(index=data.index)
        result['year'] = data.dt.year
        result['month'] = data.dt.month
        result['day'] = data.dt.day
        result['dayofweek'] = data.dt.dayofweek
        result['hour'] = data.dt.hour
        return result
    else:
        raise ValueError(f"Invalid transformation: {transformation}")

def validate_and_transform_feature(
    data: pd.Series,
    config: Dict[str, Any]
) -> Union[pd.Series, pd.DataFrame]:
    """Valida e transforma feature."""
    feature_type = config.get("type")
    transformation = config.get("transformation", {}).get("type")
    validation_rules = config.get("validation_rules", {})
    
    # Aplica regras de validação e transformação
    if feature_type == "numeric":
        min_value = validation_rules.get("min_value")
        max_value = validation_rules.get("max_value")
        handle_nulls = validation_rules.get("handle_nulls")
        handle_outliers = validation_rules.get("handle_outliers", False)
        
        if min_value is not None:
            data = data[data >= min_value]
        if max_value is not None:
            data = data[data <= max_value]
        
        return process_numeric_feature(
            data,
            transformation=transformation,
            handle_nulls=handle_nulls,
            handle_outliers=handle_outliers
        )
    
    elif feature_type == "categorical":
        categorical_values = validation_rules.get("categorical_values")
        handle_nulls = validation_rules.get("handle_nulls")
        handle_rare = validation_rules.get("handle_rare", False)
        
        if categorical_values:
            data = data[data.isin(categorical_values) | data.isna()]
        
        return process_categorical_feature(
            data,
            transformation=transformation,
            handle_nulls=handle_nulls,
            handle_rare=handle_rare
        )
    
    elif feature_type == "temporal":
        min_date = validation_rules.get("min_date")
        max_date = validation_rules.get("max_date")
        handle_nulls = validation_rules.get("handle_nulls")
        
        if min_date:
            min_date = pd.to_datetime(min_date)
            data = data[data >= min_date]
        if max_date:
            max_date = pd.to_datetime(max_date)
            data = data[data <= max_date]
        
        return process_temporal_feature(
            data,
            transformation=transformation,
            handle_nulls=handle_nulls
        )
    
    else:
        raise ValueError(f"Invalid feature type: {feature_type}")
