import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from pymongo import MongoClient
import redis

def generate_demo_data():
    print("Conectando aos serviços...")
    
    # Conectar ao MongoDB
    mongodb = MongoClient(os.getenv("MONGODB_URI", "mongodb://mongodb:27017/fstore"))
    db = mongodb['fstore']
    
    # Conectar ao Redis
    redis_client = redis.from_url(os.getenv("REDIS_URI", "redis://redis:6379/0"))
    
    print("Gerando dados de demonstração...")
    
    # Criar feature group
    feature_group = {
        "name": "Customer Metrics",
        "description": "Métricas de clientes para análise",
        "entity_id": "customer_id",
        "tags": ["demo", "customer"]
    }
    
    print("Inserindo feature group...")
    result = db.feature_groups.insert_one(feature_group)
    print(f"Feature group inserido com ID: {result.inserted_id}")
    group_id = str(result.inserted_id)
    
    # Verificar se o feature group foi realmente inserido
    print("Verificando feature group...")
    saved_group = db.feature_groups.find_one({"_id": result.inserted_id})
    print(f"Feature group encontrado: {saved_group}")
    
    # Criar features
    features = [
        {
            "name": "total_purchases",
            "description": "Total de compras do cliente",
            "feature_group_id": group_id,
            "type": "numerical",
            "entity_id": "customer_id"
        },
        {
            "name": "average_ticket",
            "description": "Ticket médio do cliente",
            "feature_group_id": group_id,
            "type": "numerical",
            "entity_id": "customer_id"
        }
    ]
    
    for feature in features:
        print(f"Inserindo feature {feature['name']}...")
        result = db.features.insert_one(feature)
        print(f"Feature inserida com ID: {result.inserted_id}")
        
        # Verificar se a feature foi realmente inserida
        print("Verificando feature...")
        saved_feature = db.features.find_one({"_id": result.inserted_id})
        print(f"Feature encontrada: {saved_feature}")
        
        # Gerar valores para 100 clientes
        for customer_id in range(1, 101):
            value = {
                "entity_id": str(customer_id),
                "value": float(np.random.normal(100, 20)),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Salvar no Redis
            key = f"feature:{str(feature.get('_id'))}:customer_{customer_id}"
            redis_client.set(key, json.dumps(value))
    
    print("Dados de demonstração gerados com sucesso!")
    
    # Fechar conexões
    redis_client.close()
    mongodb.close()

if __name__ == "__main__":
    generate_demo_data()
