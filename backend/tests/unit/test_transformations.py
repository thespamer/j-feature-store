"""Testes unitários para transformações."""
import pytest
import pandas as pd
import numpy as np
from pandas.testing import assert_series_equal, assert_frame_equal

from app.transformations.numeric import NumericTransformation
from app.transformations.categorical import CategoricalTransformation
from app.transformations.temporal import TemporalTransformation

@pytest.fixture
def numeric_transformer():
    return NumericTransformation()

@pytest.fixture
def categorical_transformer():
    return CategoricalTransformation()

@pytest.fixture
def temporal_transformer():
    return TemporalTransformation()

@pytest.fixture
def sample_numeric_data():
    return pd.Series([1, 2, 3, 4, 5, None, 7, 8, 9, 10])

@pytest.fixture
def sample_categorical_data():
    return pd.Series(['A', 'B', 'A', 'C', None, 'B', 'D', 'A', 'B', 'C'])

@pytest.fixture
def sample_temporal_data():
    dates = pd.date_range(start='2025-01-01', periods=10)
    return pd.Series(dates)

class TestNumericTransformation:
    """Testes para transformações numéricas."""

    def test_standardize(self, numeric_transformer, sample_numeric_data):
        """Testa padronização de dados."""
        result = numeric_transformer.standardize(sample_numeric_data)
        assert isinstance(result, pd.Series)
        assert abs(result.mean()) < 1e-10  # Média próxima de 0
        assert abs(result.std() - 1) < 1e-10  # Desvio padrão próximo de 1

    def test_normalize(self, numeric_transformer, sample_numeric_data):
        """Testa normalização de dados."""
        result = numeric_transformer.normalize(sample_numeric_data)
        assert isinstance(result, pd.Series)
        assert result.min() >= 0
        assert result.max() <= 1

    def test_log_transform(self, numeric_transformer):
        """Testa transformação logarítmica."""
        data = pd.Series([1, 10, 100, 1000])
        result = numeric_transformer.log_transform(data)
        assert isinstance(result, pd.Series)
        assert all(result > 0)

    def test_handle_missing(self, numeric_transformer):
        """Testa tratamento de valores faltantes."""
        data = pd.Series([1, 2, np.nan, 4, 5])
        
        # Teste com média
        result = numeric_transformer.handle_missing(data, strategy='mean')
        assert not result.isna().any()
        assert result[2] == data.mean()
        
        # Teste com mediana
        result = numeric_transformer.handle_missing(data, strategy='median')
        assert not result.isna().any()
        assert result[2] == data.median()

    def test_clip_outliers(self, numeric_transformer, sample_numeric_data):
        """Testa remoção de outliers."""
        result = numeric_transformer.clip_outliers(sample_numeric_data)
        assert isinstance(result, pd.Series)
        assert result.min() >= sample_numeric_data.quantile(0.25) - 1.5 * (sample_numeric_data.quantile(0.75) - sample_numeric_data.quantile(0.25))
        assert result.max() <= sample_numeric_data.quantile(0.75) + 1.5 * (sample_numeric_data.quantile(0.75) - sample_numeric_data.quantile(0.25))

class TestCategoricalTransformation:
    """Testes para transformações categóricas."""

    def test_one_hot_encode(self, categorical_transformer, sample_categorical_data):
        """Testa one-hot encoding."""
        result = categorical_transformer.one_hot_encode(sample_categorical_data)
        assert isinstance(result, pd.DataFrame)
        assert result.shape[1] == len(sample_categorical_data.unique())
        assert all(result.sum(axis=1) == 1)  # Cada linha deve ter exatamente um 1

    def test_label_encode(self, categorical_transformer, sample_categorical_data):
        """Testa label encoding."""
        result = categorical_transformer.label_encode(sample_categorical_data)
        assert isinstance(result, pd.Series)
        assert result.nunique() == sample_categorical_data.nunique()

    def test_frequency_encode(self, categorical_transformer, sample_categorical_data):
        """Testa frequency encoding."""
        result = categorical_transformer.frequency_encode(sample_categorical_data)
        assert isinstance(result, pd.Series)
        assert result.min() >= 0
        assert result.max() <= 1

    def test_target_encode(self, categorical_transformer, sample_categorical_data):
        """Testa target encoding."""
        target = pd.Series(np.random.normal(0, 1, len(sample_categorical_data)))
        result = categorical_transformer.target_encode(sample_categorical_data, target)
        assert isinstance(result, pd.Series)
        assert not result.isna().any()

    def test_handle_missing(self, categorical_transformer):
        """Testa tratamento de valores faltantes."""
        data = pd.Series(['A', 'B', np.nan, 'A', 'C'])
        
        # Teste com moda
        result = categorical_transformer.handle_missing(data, strategy='mode')
        assert not result.isna().any()
        assert result[2] == 'A'  # A é a moda
        
        # Teste com nova categoria
        result = categorical_transformer.handle_missing(data, strategy='new_category')
        assert not result.isna().any()
        assert result[2] == 'MISSING'

class TestTemporalTransformation:
    """Testes para transformações temporais."""

    def test_extract_components(self, temporal_transformer, sample_temporal_data):
        """Testa extração de componentes temporais."""
        result = temporal_transformer.extract_components(sample_temporal_data)
        assert isinstance(result, pd.DataFrame)
        expected_columns = ['year', 'month', 'day', 'dayofweek', 'hour', 'minute', 'second', 'quarter', 'is_weekend']
        assert all(col in result.columns for col in expected_columns)

    def test_to_unix_timestamp(self, temporal_transformer, sample_temporal_data):
        """Testa conversão para timestamp Unix."""
        result = temporal_transformer.to_unix_timestamp(sample_temporal_data)
        assert isinstance(result, pd.Series)
        assert all(isinstance(x, (int, np.integer)) for x in result)

    def test_cyclical_encode(self, temporal_transformer, sample_temporal_data):
        """Testa codificação cíclica."""
        result = temporal_transformer.cyclical_encode(sample_temporal_data, 'month')
        assert isinstance(result, pd.DataFrame)
        assert 'month_sin' in result.columns
        assert 'month_cos' in result.columns
        assert all((result['month_sin'] >= -1) & (result['month_sin'] <= 1))
        assert all((result['month_cos'] >= -1) & (result['month_cos'] <= 1))

    def test_time_since_reference(self, temporal_transformer, sample_temporal_data):
        """Testa cálculo de tempo desde referência."""
        reference_date = pd.Timestamp('2024-12-31')
        result = temporal_transformer.time_since_reference(sample_temporal_data, reference_date)
        assert isinstance(result, pd.Series)
        assert all(result >= 0)  # Todas as datas são após a referência

    def test_time_difference(self, temporal_transformer, sample_temporal_data):
        """Testa cálculo de diferença de tempo."""
        result = temporal_transformer.time_difference(sample_temporal_data)
        assert isinstance(result, pd.Series)
        assert result.iloc[0] is pd.NA  # Primeiro valor deve ser NA
        assert all(result.iloc[1:] > 0)  # Demais valores devem ser positivos

    def test_create_time_windows(self, temporal_transformer, sample_temporal_data):
        """Testa criação de janelas de tempo."""
        result = temporal_transformer.create_time_windows(sample_temporal_data, '1D')
        assert isinstance(result, pd.Series)
        assert result.dtype == 'datetime64[ns]'

"""Testes para as transformações."""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime

from app.transformations.numeric import NumericTransformation
from app.transformations.categorical import CategoricalTransformation
from app.transformations.temporal import TemporalTransformation

@pytest.fixture
def numeric_data():
    """Dados numéricos para teste."""
    return pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])

@pytest.fixture
def categorical_data():
    """Dados categóricos para teste."""
    return pd.Series(['A', 'B', 'A', 'C', 'B'])

@pytest.fixture
def temporal_data():
    """Dados temporais para teste."""
    return pd.Series([
        datetime(2024, 1, 1),
        datetime(2024, 1, 2),
        datetime(2024, 1, 3)
    ])

class TestNumericTransformation:
    """Testes para transformações numéricas."""

    def test_standardize(self, numeric_data):
        """Testa padronização."""
        transformer = NumericTransformation()
        result = transformer.standardize(numeric_data)
        
        assert len(result) == len(numeric_data)
        assert abs(result.mean()) < 1e-10
        assert abs(result.std() - 1.0) < 1e-10

    def test_normalize(self, numeric_data):
        """Testa normalização."""
        transformer = NumericTransformation()
        result = transformer.normalize(numeric_data)
        
        assert len(result) == len(numeric_data)
        assert result.min() >= 0.0
        assert result.max() <= 1.0

    def test_log_transform(self, numeric_data):
        """Testa transformação logarítmica."""
        transformer = NumericTransformation()
        result = transformer.log_transform(numeric_data)
        
        assert len(result) == len(numeric_data)
        assert (result > 0).all()

    def test_handle_missing(self):
        """Testa tratamento de valores faltantes."""
        transformer = NumericTransformation()
        data = pd.Series([1.0, None, 3.0, None, 5.0])
        
        result_mean = transformer.handle_missing(data, strategy='mean')
        assert not result_mean.isna().any()
        assert result_mean.mean() == pytest.approx(3.0)
        
        result_median = transformer.handle_missing(data, strategy='median')
        assert not result_median.isna().any()
        assert result_median.median() == 3.0
        
        result_zero = transformer.handle_missing(data, strategy='zero')
        assert not result_zero.isna().any()
        assert (result_zero[data.isna()] == 0).all()

    def test_clip_outliers(self, numeric_data):
        """Testa remoção de outliers."""
        transformer = NumericTransformation()
        data = pd.Series([1.0, 100.0, 2.0, -50.0, 3.0])
        
        result = transformer.clip_outliers(data)
        assert result.min() > -50.0
        assert result.max() < 100.0

class TestCategoricalTransformation:
    """Testes para transformações categóricas."""

    def test_one_hot_encode(self, categorical_data):
        """Testa one-hot encoding."""
        transformer = CategoricalTransformation()
        result = transformer.one_hot_encode(categorical_data)
        
        assert isinstance(result, pd.DataFrame)
        assert result.shape[1] == len(categorical_data.unique())
        assert (result.sum(axis=1) == 1).all()

    def test_label_encode(self, categorical_data):
        """Testa label encoding."""
        transformer = CategoricalTransformation()
        result = transformer.label_encode(categorical_data)
        
        assert len(result) == len(categorical_data)
        assert result.nunique() == categorical_data.nunique()

    def test_frequency_encode(self, categorical_data):
        """Testa frequency encoding."""
        transformer = CategoricalTransformation()
        result = transformer.frequency_encode(categorical_data)
        
        assert len(result) == len(categorical_data)
        assert result.sum() == pytest.approx(1.0)

    def test_handle_missing(self):
        """Testa tratamento de valores faltantes."""
        transformer = CategoricalTransformation()
        data = pd.Series(['A', None, 'B', None, 'A'])
        
        result_mode = transformer.handle_missing(data, strategy='mode')
        assert not result_mode.isna().any()
        assert result_mode.mode()[0] == 'A'
        
        result_new = transformer.handle_missing(data, strategy='new_category')
        assert not result_new.isna().any()
        assert (result_new[data.isna()] == 'MISSING').all()

    def test_group_rare_categories(self, categorical_data):
        """Testa agrupamento de categorias raras."""
        transformer = CategoricalTransformation()
        data = pd.Series(['A', 'B', 'A', 'C', 'D', 'E', 'A'])
        
        result = transformer.group_rare_categories(data, min_freq=0.2)
        assert 'RARE' in result.unique()
        assert result.value_counts()['RARE'] >= 1

class TestTemporalTransformation:
    """Testes para transformações temporais."""

    def test_extract_components(self, temporal_data):
        """Testa extração de componentes temporais."""
        transformer = TemporalTransformation()
        result = transformer.extract_components(temporal_data)
        
        assert isinstance(result, pd.DataFrame)
        assert 'year' in result.columns
        assert 'month' in result.columns
        assert 'day' in result.columns

    def test_to_unix_timestamp(self, temporal_data):
        """Testa conversão para timestamp Unix."""
        transformer = TemporalTransformation()
        result = transformer.to_unix_timestamp(temporal_data)
        
        assert len(result) == len(temporal_data)
        assert (result > 0).all()

    def test_cyclical_encoding(self, temporal_data):
        """Testa encoding cíclico."""
        transformer = TemporalTransformation()
        result = transformer.cyclical_encoding(temporal_data, 'month')
        
        assert isinstance(result, pd.DataFrame)
        assert 'month_sin' in result.columns
        assert 'month_cos' in result.columns

    def test_time_since(self, temporal_data):
        """Testa cálculo de tempo desde referência."""
        transformer = TemporalTransformation()
        reference = datetime(2024, 1, 1)
        result = transformer.time_since(temporal_data, reference)
        
        assert len(result) == len(temporal_data)
        assert (result >= 0).all()
