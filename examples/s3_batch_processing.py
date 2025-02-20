from fstore import FeatureStore
from fstore.connectors import S3Connector
import pandas as pd

# Inicializar o Feature Store
store = FeatureStore()

# Configurar o conector S3
s3_config = {
    "aws_access_key_id": "your_access_key",
    "aws_secret_access_key": "your_secret_key",
    "region_name": "us-east-1",
    "bucket": "my-feature-store-bucket"
}

# Criar uma conexão com S3
connector = S3Connector(s3_config)

# Registrar uma feature que será processada em batch do S3
feature = store.create_feature(
    name="customer_lifetime_value",
    description="Valor total gasto pelo cliente desde o início",
    entity_id="customer_id",
    feature_group="customer_metrics",
    type="numerical",
    batch_config={
        "path": "customer_transactions/",
        "file_pattern": "*.parquet",
        "processing_schedule": "0 0 * * *"  # Executar diariamente à meia-noite
    }
)

# Função de processamento em batch
def process_batch(df):
    # Agregar transações por cliente
    result = df.groupby('customer_id')['transaction_amount'].sum().reset_index()
    result.columns = ['customer_id', 'lifetime_value']
    return result

# Configurar e iniciar o processamento em batch
store.configure_batch_processing(
    feature_name="customer_lifetime_value",
    connector=connector,
    process_fn=process_batch
)

# Executar o processamento em batch manualmente
store.run_batch_processing("customer_lifetime_value")

# Buscar os valores processados
values = store.get_feature_values(
    feature_names=["customer_lifetime_value"],
    entity_ids=["123", "456", "789"]
)
