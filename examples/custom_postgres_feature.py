from fstore.connectors import PostgreSQLConnector
from fstore import FeatureStore

def register_custom_postgres_feature():
    # 1. Configurar conexão com PostgreSQL
    postgres_config = {
        "host": "localhost",  # ou seu host
        "port": 5432,        # sua porta
        "database": "mydb",  # seu database
        "user": "user",      # seu usuário
        "password": "pass"   # sua senha
    }

    # 2. Inicializar o Feature Store e o conector
    store = FeatureStore()
    pg_connector = PostgreSQLConnector(postgres_config)

    # 3. Definir a feature com sua query customizada
    feature_definition = {
        "name": "customer_purchase_frequency",
        "description": "Frequência de compras do cliente nos últimos 30 dias",
        "entity_id": "customer",
        "feature_group": "customer_metrics",
        "query": """
            WITH customer_purchases AS (
                SELECT 
                    customer_id,
                    COUNT(*) as purchase_count,
                    COUNT(*) / 30.0 as purchase_frequency
                FROM orders
                WHERE created_at >= NOW() - INTERVAL '30 days'
                GROUP BY customer_id
            )
            SELECT 
                customer_id as entity_id,
                purchase_frequency as value,
                NOW() as timestamp
            FROM customer_purchases
        """,
        "schedule": "0 0 * * *"  # Executa diariamente à meia-noite
    }

    # 4. Registrar a feature
    store.register_feature(
        feature_definition,
        connector=pg_connector
    )

    return feature_definition["name"]

if __name__ == "__main__":
    feature_name = register_custom_postgres_feature()
    print(f"Feature '{feature_name}' registrada com sucesso!")
