# Workflows de Machine Learning com FStore

Este guia detalha os workflows comuns de ML usando a FStore Feature Store.

## Sumário
- [Preparação de Dados](#preparação-de-dados)
- [Treinamento](#treinamento)
- [Validação](#validação)
- [Produção](#produção)

## Preparação de Dados

### 1. Feature Engineering

```python
from fstore import FeatureStore
from fstore.transformations import WindowAggregator, Encoder

# Criar features agregadas
agg = WindowAggregator(
    window_size="30d",
    aggregations=["mean", "sum", "count"]
)

store = FeatureStore()
store.create_feature_group(
    name="customer_behavior",
    source_table="transactions",
    transformations=[agg],
    entity="customer"
)

# Encoding de variáveis categóricas
encoder = Encoder(method="target_encoding")
store.add_transformation(
    feature="customer_category",
    transformation=encoder
)
```

### 2. Feature Selection

```python
from fstore.analysis import FeatureSelector

selector = FeatureSelector()

# Análise de correlação
corr_matrix = selector.correlation_analysis(
    feature_group="customer_behavior"
)

# Importância de features
important_features = selector.select_features(
    method="mutual_info",
    target="conversion",
    top_k=10
)
```

## Treinamento

### 1. Criação de Training Dataset

```python
# Point-in-time correct feature extraction
training_data = store.get_training_features(
    feature_list=[
        "customer_behavior:*",  # todas as features do grupo
        "product_features:price",
        "product_features:category"
    ],
    start_date="2024-01-01",
    end_date="2024-02-01",
    entity_df=transactions_df,
    timestamp_column="transaction_date"
)

# Split treino/teste preservando ordem temporal
from fstore.utils import temporal_split

train_df, test_df = temporal_split(
    training_data,
    test_size=0.2,
    timestamp_column="transaction_date"
)
```

### 2. Feature Versioning

```python
# Registrar versão do feature set
feature_set = store.create_feature_set(
    name="fraud_detection_v1",
    features=important_features,
    metadata={
        "author": "team_ml",
        "purpose": "fraud_detection",
        "model_version": "1.0"
    }
)

# Exportar feature set
store.export_feature_set(
    feature_set.id,
    format="parquet",
    path="s3://my-bucket/features/"
)
```

## Validação

### 1. Quality Checks

```python
from fstore.validation import FeatureValidator

validator = FeatureValidator()

# Definir expectativas
validator.add_expectation(
    "purchase_amount",
    {
        "min_value": 0,
        "max_value": 10000,
        "null_percentage": 0.01
    }
)

# Validar features
validation_results = validator.validate_features(
    feature_set.id
)
```

### 2. Drift Detection

```python
from fstore.monitoring import DriftMonitor

monitor = DriftMonitor()

# Configurar baseline
monitor.set_baseline(
    feature_set.id,
    start_date="2024-01-01",
    end_date="2024-01-31"
)

# Detectar drift
drift_report = monitor.check_drift(
    current_data=test_df,
    method="ks_test",
    threshold=0.05
)
```

## Produção

### 1. Online Serving

```python
# Configurar serving
store.configure_online_serving(
    feature_set.id,
    update_frequency="1h",
    cache_ttl="30m"
)

# Servir features
online_features = store.get_online_features(
    feature_set.id,
    entity_keys=["customer_123"]
)
```

### 2. Monitoramento

```python
from fstore.monitoring import FeatureMonitor

monitor = FeatureMonitor()

# Configurar métricas
monitor.add_metric(
    "missing_values",
    threshold=0.05,
    alert_channel="slack"
)

# Iniciar monitoramento
monitor.start_monitoring(
    feature_set.id,
    frequency="1h"
)
```

### 3. A/B Testing

```python
# Configurar teste A/B de features
from fstore.experimentation import ABTest

test = ABTest(
    name="new_features_test",
    feature_sets={
        "control": "fraud_detection_v1",
        "treatment": "fraud_detection_v2"
    },
    metrics=["auc", "precision", "recall"],
    duration="7d"
)

# Iniciar teste
test.start()

# Verificar resultados
results = test.get_results()
```

## Melhores Práticas

1. **Versionamento**
   - Sempre versione seus feature sets
   - Mantenha metadata detalhado
   - Use tags para organização

2. **Validação**
   - Implemente checks de qualidade
   - Monitore drift constantemente
   - Valide transformações

3. **Performance**
   - Use caching apropriadamente
   - Otimize queries de feature engineering
   - Monitore latência de serving

4. **Governança**
   - Documente todas as features
   - Mantenha linhagem de dados
   - Implemente controles de acesso
