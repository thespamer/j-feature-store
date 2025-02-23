import asyncio
import aiohttp
import json
from datetime import datetime

async def create_feature_group(session, group_data):
    async with session.post('http://localhost:8000/api/v1/feature-groups/', json=group_data) as response:
        return await response.json()

async def create_feature(session, feature_data):
    async with session.post('http://localhost:8000/api/v1/features/', json=feature_data) as response:
        return await response.json()

async def main():
    # Dados de exemplo
    customer_metrics = {
        "name": "Customer Metrics",
        "description": "Métricas de clientes para análise",
        "entity_id": "customer",
        "entity_type": "customer",
        "tags": ["customer", "metrics"],
        "frequency": "daily"
    }

    transaction_metrics = {
        "name": "Transaction Metrics",
        "description": "Métricas de transações",
        "entity_id": "transaction",
        "entity_type": "transaction",
        "tags": ["transaction", "metrics"],
        "frequency": "real-time"
    }

    async with aiohttp.ClientSession() as session:
        # Criar grupos de features
        print("Criando grupos de features...")
        customer_group = await create_feature_group(session, customer_metrics)
        transaction_group = await create_feature_group(session, transaction_metrics)

        # Features para o grupo Customer Metrics
        customer_features = [
            {
                "name": "total_purchases",
                "description": "Total de compras do cliente",
                "feature_group_id": customer_group["id"],
                "type": "float",
                "entity_id": "customer",
                "tags": ["financial", "customer"]
            },
            {
                "name": "average_ticket",
                "description": "Ticket médio do cliente",
                "feature_group_id": customer_group["id"],
                "type": "float",
                "entity_id": "customer",
                "tags": ["financial", "customer"]
            },
            {
                "name": "last_purchase_date",
                "description": "Data da última compra",
                "feature_group_id": customer_group["id"],
                "type": "datetime",
                "entity_id": "customer",
                "tags": ["temporal", "customer"]
            }
        ]

        # Features para o grupo Transaction Metrics
        transaction_features = [
            {
                "name": "transaction_amount",
                "description": "Valor da transação",
                "feature_group_id": transaction_group["id"],
                "type": "float",
                "entity_id": "transaction",
                "tags": ["financial", "transaction"]
            },
            {
                "name": "payment_method",
                "description": "Método de pagamento",
                "feature_group_id": transaction_group["id"],
                "type": "string",
                "entity_id": "transaction",
                "tags": ["categorical", "transaction"]
            },
            {
                "name": "transaction_timestamp",
                "description": "Data e hora da transação",
                "feature_group_id": transaction_group["id"],
                "type": "datetime",
                "entity_id": "transaction",
                "tags": ["temporal", "transaction"]
            }
        ]

        # Criar features para cada grupo
        print("\nCriando features para Customer Metrics...")
        for feature in customer_features:
            try:
                result = await create_feature(session, feature)
                print(f"Created feature: {result['name']}")
            except Exception as e:
                print(f"Error creating feature {feature['name']}: {e}")

        print("\nCriando features para Transaction Metrics...")
        for feature in transaction_features:
            try:
                result = await create_feature(session, feature)
                print(f"Created feature: {result['name']}")
            except Exception as e:
                print(f"Error creating feature {feature['name']}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
