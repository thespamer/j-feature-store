import asyncio
import aiohttp
import json
from datetime import datetime

async def delete_feature(session, feature_id):
    async with session.delete(f'http://localhost:8000/api/v1/features/{feature_id}') as response:
        if response.status == 200:
            print(f"Feature {feature_id} deletada com sucesso")
        else:
            print(f"Erro ao deletar feature {feature_id}:", await response.text())

async def delete_feature_group(session, group_id):
    async with session.delete(f'http://localhost:8000/api/v1/feature-groups/{group_id}') as response:
        if response.status == 200:
            print(f"Grupo {group_id} deletado com sucesso")
        else:
            print(f"Erro ao deletar grupo {group_id}:", await response.text())

async def get_all_features(session):
    async with session.get('http://localhost:8000/api/v1/features/') as response:
        return await response.json()

async def get_all_feature_groups(session):
    async with session.get('http://localhost:8000/api/v1/feature-groups/') as response:
        return await response.json()

async def delete_all_data(session):
    print("\nObtendo todas as features...")
    features = await get_all_features(session)
    for feature in features:
        await delete_feature(session, feature['id'])

    print("\nObtendo todos os grupos...")
    groups = await get_all_feature_groups(session)
    for group in groups:
        await delete_feature_group(session, group['id'])

async def create_feature_group(session, group_data):
    async with session.post('http://localhost:8000/api/v1/feature-groups/', json=group_data) as response:
        result = await response.json()
        if 'id' not in result:  # Verifica se a resposta tem um ID
            print("Erro ao criar grupo:", result)
            return None
        print("Grupo criado:", result)
        return result

async def create_feature(session, feature_data):
    async with session.post('http://localhost:8000/api/v1/features/', json=feature_data) as response:
        result = await response.json()
        if 'id' not in result:  # Verifica se a resposta tem um ID
            print("Erro ao criar feature:", result)
            return None
        return result

async def main():
    async with aiohttp.ClientSession() as session:
        # Primeiro, limpar todos os dados existentes
        print("\nLimpando dados existentes...")
        await delete_all_data(session)
        
        print("\nCriando novos dados...")
        # Dados de exemplo
        customer_metrics = {
            "name": "Customer Metrics",
            "description": "Métricas de clientes para análise",
            "entity_type": "customer",
            "features": [],
            "metadata": {
                "frequency": "daily",
                "tags": ["customer", "metrics"]
            }
        }

        transaction_metrics = {
            "name": "Transaction Metrics",
            "description": "Métricas de transações",
            "entity_type": "transaction",
            "features": [],
            "metadata": {
                "frequency": "real-time",
                "tags": ["transaction", "metrics"]
            }
        }

        # Criar grupos de features
        print("\nCriando grupos de features...")
        customer_group = await create_feature_group(session, customer_metrics)
        if not customer_group or 'id' not in customer_group:
            print("Erro ao criar grupo de clientes")
            return
            
        customer_group_id = customer_group['id']
        print(f"ID do grupo de clientes: {customer_group_id}")
            
        transaction_group = await create_feature_group(session, transaction_metrics)
        if not transaction_group or 'id' not in transaction_group:
            print("Erro ao criar grupo de transações")
            return
            
        transaction_group_id = transaction_group['id']
        print(f"ID do grupo de transações: {transaction_group_id}")

        # Features para o grupo Customer Metrics
        customer_features = [
            {
                "name": "total_purchases",
                "description": "Total de compras do cliente",
                "type": "numeric",
                "entity_id": "customer_001",
                "feature_group_id": customer_group_id,
                "metadata": {
                    "unit": "count",
                    "tags": ["financial", "customer"]
                }
            },
            {
                "name": "average_ticket",
                "description": "Ticket médio do cliente",
                "type": "numeric",
                "entity_id": "customer_001",
                "feature_group_id": customer_group_id,
                "metadata": {
                    "unit": "BRL",
                    "tags": ["financial", "customer"]
                }
            },
            {
                "name": "last_purchase_date",
                "description": "Data da última compra",
                "type": "temporal",
                "entity_id": "customer_001",
                "feature_group_id": customer_group_id,
                "metadata": {
                    "tags": ["temporal", "customer"]
                }
            }
        ]

        # Features para o grupo Transaction Metrics
        transaction_features = [
            {
                "name": "transaction_amount",
                "description": "Valor da transação",
                "type": "numeric",
                "entity_id": "transaction_001",
                "feature_group_id": transaction_group_id,
                "metadata": {
                    "unit": "BRL",
                    "tags": ["financial", "transaction"]
                }
            },
            {
                "name": "payment_method",
                "description": "Método de pagamento",
                "type": "categorical",
                "entity_id": "transaction_001",
                "feature_group_id": transaction_group_id,
                "metadata": {
                    "tags": ["categorical", "transaction"]
                }
            },
            {
                "name": "transaction_datetime",
                "description": "Data e hora da transação",
                "type": "temporal",
                "entity_id": "transaction_001",
                "feature_group_id": transaction_group_id,
                "metadata": {
                    "tags": ["temporal", "transaction"]
                }
            }
        ]

        # Criar features
        print("\nCriando features para o grupo Customer Metrics...")
        for feature in customer_features:
            try:
                result = await create_feature(session, feature)
                if result:
                    print(f"Feature criada: {result.get('name')}")
            except Exception as e:
                print(f"Erro ao criar feature {feature['name']}: {e}")

        print("\nCriando features para o grupo Transaction Metrics...")
        for feature in transaction_features:
            try:
                result = await create_feature(session, feature)
                if result:
                    print(f"Feature criada: {result.get('name')}")
            except Exception as e:
                print(f"Erro ao criar feature {feature['name']}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
