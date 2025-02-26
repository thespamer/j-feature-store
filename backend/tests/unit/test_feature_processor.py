"""Testes para o processador de features."""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime

from app.core.feature_processor import (
    process_numeric_feature,
    process_categorical_feature,
    process_temporal_feature,
    validate_and_transform_feature,
    handle_missing_values,
    handle_outliers
)

@pytest.fixture
def numeric_data():
    """Fixture para dados numéricos."""
    return pd.Series([1.0, 2.0, 3.0, 4.0, 5.0, np.nan, 100.0])

@pytest.fixture
def categorical_data():
    """Fixture para dados categóricos."""
    return pd.Series(['A', 'B', 'A', 'C', 'B', None, 'D', 'E'])

@pytest.fixture
def temporal_data():
    """Fixture para dados temporais."""
    return pd.Series([
        datetime(2024, 1, 1),
        datetime(2024, 1, 2),
        datetime(2024, 1, 3),
        None,
        datetime(2024, 1, 5)
    ])

def test_handle_missing_values():
    """Testa tratamento de valores faltantes."""
    # Dados numéricos
    data = pd.Series([1.0, 2.0, np.nan, 4.0, 5.0])
    
    # Teste com média
    result = handle_missing_values(data, strategy="mean")
    assert not result.isna().any()
    assert result[2] == pytest.approx(data.mean())
    
    # Teste com mediana
    result = handle_missing_values(data, strategy="median")
    assert not result.isna().any()
    assert result[2] == pytest.approx(data.median())
    
    # Teste com moda
    result = handle_missing_values(data, strategy="mode")
    assert not result.isna().any()
    
    # Teste com valor constante
    result = handle_missing_values(data, strategy="constant", fill_value=0.0)
    assert not result.isna().any()
    assert result[2] == 0.0
    
    # Teste com forward fill
    result = handle_missing_values(data, strategy="ffill")
    assert not result.isna().any()
    assert result[2] == 2.0
    
    # Teste com backward fill
    result = handle_missing_values(data, strategy="bfill")
    assert not result.isna().any()
    assert result[2] == 4.0
    
    # Teste com estratégia inválida
    with pytest.raises(ValueError):
        handle_missing_values(data, strategy="invalid")

def test_handle_outliers():
    """Testa tratamento de outliers."""
    # Dados com outliers
    data = pd.Series([1.0, 2.0, 3.0, 100.0, -100.0])
    
    # Teste com z-score
    result = handle_outliers(data, method="zscore", threshold=2.0)
    assert len(result) == len(data)
    assert result.max() < 100.0
    assert result.min() > -100.0
    
    # Teste com IQR
    result = handle_outliers(data, method="iqr", threshold=1.5)
    assert len(result) == len(data)
    assert result.max() < 100.0
    assert result.min() > -100.0
    
    # Teste com percentil
    result = handle_outliers(data, method="percentile", threshold=0.95)
    assert len(result) == len(data)
    assert result.max() < 100.0
    assert result.min() > -100.0
    
    # Teste com método inválido
    with pytest.raises(ValueError):
        handle_outliers(data, method="invalid")

def test_process_numeric_feature(numeric_data):
    """Testa processamento de feature numérica."""
    # Teste com standard scaler
    result = process_numeric_feature(
        numeric_data,
        transformation="standard_scaler",
        handle_nulls="mean",
        handle_outliers=True
    )
    assert not result.isna().any()
    assert abs(result.mean()) < 1e-10
    assert abs(result.std() - 1.0) < 1e-10
    
    # Teste com min-max scaler
    result = process_numeric_feature(
        numeric_data,
        transformation="min_max_scaler",
        handle_nulls="median",
        handle_outliers=True
    )
    assert not result.isna().any()
    assert result.min() >= 0.0
    assert result.max() <= 1.0
    
    # Teste com log transform
    result = process_numeric_feature(
        numeric_data,
        transformation="log_transform",
        handle_nulls="constant",
        handle_outliers=False
    )
    assert not result.isna().any()
    assert (result >= 0).all()
    
    # Teste com transformação inválida
    with pytest.raises(ValueError):
        process_numeric_feature(numeric_data, transformation="invalid")

def test_process_categorical_feature(categorical_data):
    """Testa processamento de feature categórica."""
    # Teste com one-hot encoding
    result = process_categorical_feature(
        categorical_data,
        transformation="one_hot",
        handle_nulls="constant",
        handle_rare=True
    )
    assert isinstance(result, pd.DataFrame)
    assert not result.isna().any().any()
    assert (result.isin([0, 1])).all().all()
    
    # Teste com label encoding
    result = process_categorical_feature(
        categorical_data,
        transformation="label_encoding",
        handle_nulls="constant",
        handle_rare=True
    )
    assert isinstance(result, pd.Series)
    assert not result.isna().any()
    assert result.dtype in ['int32', 'int64']
    
    # Teste com transformação inválida
    with pytest.raises(ValueError):
        process_categorical_feature(categorical_data, transformation="invalid")

def test_process_temporal_feature(temporal_data):
    """Testa processamento de feature temporal."""
    # Teste com timestamp
    result = process_temporal_feature(
        temporal_data,
        transformation="timestamp",
        handle_nulls="ffill"
    )
    assert isinstance(result, pd.Series)
    assert not result.isna().any()
    assert result.dtype in ['int32', 'int64', 'float32', 'float64']
    
    # Teste com date parts
    result = process_temporal_feature(
        temporal_data,
        transformation="date_parts",
        handle_nulls="bfill"
    )
    assert isinstance(result, pd.DataFrame)
    assert not result.isna().any().any()
    assert 'year' in result.columns
    assert 'month' in result.columns
    assert 'day' in result.columns
    assert 'dayofweek' in result.columns
    assert 'hour' in result.columns
    
    # Teste com transformação inválida
    with pytest.raises(ValueError):
        process_temporal_feature(temporal_data, transformation="invalid")

def test_validate_and_transform_feature():
    """Testa validação e transformação de feature."""
    # Teste com feature numérica
    numeric_data = pd.Series([1.0, 2.0, 3.0, np.nan, 100.0])
    numeric_config = {
        "type": "numeric",
        "transformation": {
            "type": "standard_scaler"
        },
        "validation_rules": {
            "min_value": 0,
            "max_value": 1000,
            "handle_nulls": "mean",
            "handle_outliers": True
        }
    }
    result = validate_and_transform_feature(numeric_data, numeric_config)
    assert isinstance(result, pd.Series)
    assert not result.isna().any()
    
    # Teste com feature categórica
    categorical_data = pd.Series(['A', 'B', 'A', None, 'C'])
    categorical_config = {
        "type": "categorical",
        "transformation": {
            "type": "one_hot"
        },
        "validation_rules": {
            "categorical_values": ['A', 'B', 'C'],
            "handle_nulls": "constant",
            "handle_rare": True
        }
    }
    result = validate_and_transform_feature(categorical_data, categorical_config)
    assert isinstance(result, pd.DataFrame)
    assert not result.isna().any().any()
    
    # Teste com feature temporal
    temporal_data = pd.Series([
        datetime(2024, 1, 1),
        datetime(2024, 1, 2),
        None,
        datetime(2024, 1, 4)
    ])
    temporal_config = {
        "type": "temporal",
        "transformation": {
            "type": "date_parts"
        },
        "validation_rules": {
            "min_date": "2024-01-01",
            "max_date": "2024-12-31",
            "handle_nulls": "ffill"
        }
    }
    result = validate_and_transform_feature(temporal_data, temporal_config)
    assert isinstance(result, pd.DataFrame)
    assert not result.isna().any().any()
    
    # Teste com tipo inválido
    invalid_config = {
        "type": "invalid",
        "transformation": {
            "type": "none"
        }
    }
    with pytest.raises(ValueError):
        validate_and_transform_feature(numeric_data, invalid_config)
