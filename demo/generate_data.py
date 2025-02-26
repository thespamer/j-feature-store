import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from pymongo import MongoClient
from bson import ObjectId
import redis

def generate_demo_data():
    print("Conectando aos serviços...")
    
    # Conectar ao MongoDB
    mongodb = MongoClient(os.getenv("MONGODB_URI", "mongodb://mongodb:27017"))
    db = mongodb['feature_store']
    
    # Conectar ao Redis
    redis_client = redis.from_url(os.getenv("REDIS_URI", "redis://redis:6379/0"))
    
    print("Limpando dados antigos...")
    db.feature_groups.delete_many({})
    db.features.delete_many({})
    redis_client.flushall()
    
    print("Gerando dados de demonstração...")
    
    # Criar feature group
    feature_group = {
        "name": "Customer Metrics",
        "description": "Métricas de clientes para análise",
        "entity_id": "customer_id",
        "entity_type": "customer",
        "tags": ["demo", "customer"],
        "features": [],
        "created_at": datetime.utcnow(),
        "version": 1
    }
    
    print("Inserindo feature group...")
    result = db.feature_groups.insert_one(feature_group)
    print(f"Feature group inserido com ID: {result.inserted_id}")
    group_id = str(result.inserted_id)
    
    # Verificar se o feature group foi realmente inserido
    print("Verificando feature group...")
    saved_group = db.feature_groups.find_one({"_id": ObjectId(result.inserted_id)})
    print(f"Feature group encontrado: {saved_group}")
    
    # Criar features
    features = [
        {
            "name": "total_purchases",
            "description": "Total de compras do cliente",
            "feature_group_id": group_id,
            "type": "numerical",
            "entity_id": "customer_id",
            "metadata": {
                "owner": "system",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "tags": ["demo", "customer", "purchases"],
                "description": "Total de compras do cliente"
            },
            "validation_rules": {
                "allow_null": False,
                "min_value": 0
            },
            "created_at": datetime.utcnow(),
            "version": "1.0.0",
            "status": "active"
        },
        {
            "name": "average_ticket",
            "description": "Ticket médio do cliente",
            "feature_group_id": group_id,
            "type": "numerical",
            "entity_id": "customer_id",
            "metadata": {
                "owner": "system",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "tags": ["demo", "customer", "purchases"],
                "description": "Ticket médio do cliente"
            },
            "validation_rules": {
                "allow_null": False,
                "min_value": 0
            },
            "created_at": datetime.utcnow(),
            "version": "1.0.0",
            "status": "active"
        }
    ]
    
    feature_ids = []
    for feature in features:
        print(f"Inserindo feature {feature['name']}...")
        result = db.features.insert_one(feature)
        feature_id = str(result.inserted_id)
        feature_ids.append(feature_id)
        print(f"Feature inserida com ID: {feature_id}")
        
        print("Verificando feature...")
        saved_feature = db.features.find_one({"_id": ObjectId(result.inserted_id)})
        print(f"Feature encontrada: {saved_feature}")
        
        # Gerar valores para 100 clientes
        for customer_id in range(1, 101):
            value = {
                "entity_id": str(customer_id),
                "value": np.random.randint(1, 100) if feature["name"] == "total_purchases" else round(np.random.uniform(10.0, 1000.0), 2),
                "timestamp": datetime.utcnow().isoformat()
            }
            redis_client.hset(f"feature:{feature_id}", str(customer_id), json.dumps(value))
    
    # Atualizar o feature group com os IDs das features
    db.feature_groups.update_one(
        {"_id": ObjectId(result.inserted_id)},
        {"$set": {"features": feature_ids}}
    )
    
    print("Dados de demonstração gerados com sucesso!")

if __name__ == "__main__":
    generate_demo_data()
