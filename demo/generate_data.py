import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from pymongo import MongoClient
from bson import ObjectId
import redis
import shutil

def read_sql_file(filename):
    """Lê o conteúdo de um arquivo SQL."""
    with open(filename, 'r') as f:
        return f.read()

def copy_demo_files():
    print("Copiando arquivos de demonstração...")
    
    # Criar diretórios se não existirem
    os.makedirs("/app/data/transformations", exist_ok=True)
    os.makedirs("/app/data/pipelines", exist_ok=True)
    
    # Copiar arquivos de demonstração
    shutil.copy2("/app/transformations/customer_features.sql", "/app/data/transformations/")
    shutil.copy2("/app/pipelines/customer_pipeline.json", "/app/data/pipelines/")

def generate_demo_data():
    print("Conectando aos serviços...")
    
    # Conectar ao MongoDB
    mongodb = MongoClient(os.getenv("MONGODB_URL", "mongodb://mongodb:27017"))
    db = mongodb[os.getenv("MONGODB_DB", "feature_store")]
    
    # Conectar ao Redis
    redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379/0"))
    
    print("Limpando dados antigos...")
    db.feature_groups.delete_many({})
    db.features.delete_many({})
    db.pipelines.delete_many({})
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
    
    # Ler SQL de transformação
    sql_transform = read_sql_file("/app/transformations/customer_features.sql")
    
    # Criar features
    features = [
        {
            "name": "total_orders",
            "description": "Total de pedidos do cliente",
            "feature_group_id": group_id,
            "type": "numerical",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "version": "1.0.0",
            "status": "active",
            "metadata": {
                "tags": ["demo", "customer", "orders"]
            },
            "transformation": {
                "type": "sql",
                "params": {
                    "query": sql_transform,
                    "output_column": "total_orders"
                }
            }
        },
        {
            "name": "total_spent",
            "description": "Valor total gasto pelo cliente",
            "feature_group_id": group_id,
            "type": "numerical",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "version": "1.0.0",
            "status": "active",
            "metadata": {
                "tags": ["demo", "customer", "financial"]
            },
            "transformation": {
                "type": "sql",
                "params": {
                    "query": sql_transform,
                    "output_column": "total_spent"
                }
            }
        },
        {
            "name": "avg_order_value",
            "description": "Valor médio dos pedidos",
            "feature_group_id": group_id,
            "type": "numerical",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "version": "1.0.0",
            "status": "active",
            "metadata": {
                "tags": ["demo", "customer", "financial"]
            },
            "transformation": {
                "type": "sql",
                "params": {
                    "query": sql_transform,
                    "output_column": "avg_order_value"
                }
            }
        }
    ]
    
    print("Inserindo features...")
    result = db.features.insert_many(features)
    print(f"Features inseridas: {len(result.inserted_ids)}")
    
    # Atualizar feature group com os IDs das features
    feature_ids = [str(id) for id in result.inserted_ids]
    db.feature_groups.update_one(
        {"_id": ObjectId(group_id)},
        {"$set": {"features": feature_ids}}
    )
    
    # Criar pipeline de exemplo
    pipeline = {
        "name": "Customer Metrics Pipeline",
        "feature_group_id": group_id,
        "config": {
            "source": {
                "type": "postgresql",
                "config": {
                    "table": "customers",
                    "join_tables": ["orders", "order_items"],
                    "incremental_field": "updated_at"
                }
            },
            "transformations": [
                {
                    "type": "sql",
                    "name": "customer_features",
                    "file": "/app/data/transformations/customer_features.sql"
                }
            ],
            "schedule": {
                "interval": "daily",
                "start_time": "00:00:00"
            }
        },
        "created_at": datetime.utcnow(),
        "status": "pending"
    }
    
    print("Inserindo pipeline...")
    result = db.pipelines.insert_one(pipeline)
    print(f"Pipeline inserido com ID: {result.inserted_id}")
    
    # Copiar arquivos de demonstração
    copy_demo_files()
    
    print("Dados de demonstração gerados com sucesso!")

if __name__ == "__main__":
    generate_demo_data()
