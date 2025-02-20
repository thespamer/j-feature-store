from fstore import FeatureStore
from fstore.connectors import PostgresConnector

# Inicializar o Feature Store
store = FeatureStore()

# Configurar o conector PostgreSQL
postgres_config = {
    "host": "localhost",
    "port": 5432,
    "database": "mydatabase",
    "user": "myuser",
    "password": "mypassword"
}

# Criar uma conexão com PostgreSQL
connector = PostgresConnector(postgres_config)

# Registrar uma feature do PostgreSQL
feature = store.create_feature(
    name="customer_total_purchases",
    description="Total de compras do cliente nos últimos 30 dias",
    entity_id="customer_id",
    feature_group="customer_metrics",
    type="numerical",
    query="""
        SELECT 
            customer_id,
            SUM(purchase_amount) as total_purchases
        FROM customer_purchases
        WHERE purchase_date >= NOW() - INTERVAL '30 days'
        GROUP BY customer_id
    """
)

# Atualizar os valores da feature
store.update_feature_values(
    feature_name="customer_total_purchases",
    connector=connector
)

# Buscar valores da feature para um conjunto de entidades
values = store.get_feature_values(
    feature_names=["customer_total_purchases"],
    entity_ids=["123", "456", "789"]
)
