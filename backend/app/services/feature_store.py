from typing import List, Optional
from datetime import datetime
import json
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as redis
from app.models.feature import Feature, FeatureGroup, FeatureValue
from app.core.config import settings
from fastapi import HTTPException

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

class FeatureStore:
    def __init__(self):
        """
        Inicializa a conexão com o MongoDB
        """
        self.client = None
        self.db = None
        self.redis = None

    async def initialize(self):
        """Inicializa as conexões de forma assíncrona"""
        try:
            print("Conectando ao MongoDB...")
            self.client = AsyncIOMotorClient('mongodb://mongodb:27017')
            print("Conexão estabelecida, selecionando banco de dados 'fstore'...")
            self.db = self.client.fstore

            print("Conectando ao Redis...")
            self.redis = redis.from_url('redis://redis:6379/0')
            print("Conexão com Redis estabelecida com sucesso")

            print("Conexão com MongoDB estabelecida com sucesso")
        except Exception as e:
            print(f"Erro ao conectar com MongoDB: {e}")
            raise

    async def create_feature(self, feature: Feature) -> Feature:
        """
        Cria uma nova feature
        """
        try:
            # Salva no MongoDB
            feature_dict = feature.model_dump(exclude={'id'})
            result = await self.db.features.insert_one(feature_dict)
            feature.id = str(result.inserted_id)

            # Salva no Redis
            redis_key = f"feature:{feature.id}"
            await self.redis.set(redis_key, json.dumps(feature.model_dump(), cls=CustomEncoder))

            return feature
        except Exception as e:
            print(f"Error creating feature: {e}")
            raise

    async def list_features(self, entity_id: Optional[str] = None) -> List[Feature]:
        """
        Lista todas as features
        """
        try:
            query = {"entity_id": entity_id} if entity_id else {}
            cursor = self.db.features.find(query)
            features = []
            async for doc in cursor:
                doc['id'] = str(doc.pop('_id'))
                features.append(Feature(**doc))
            return features
        except Exception as e:
            print(f"Error listing features: {e}")
            raise

    async def get_feature(self, feature_id: str) -> Optional[Feature]:
        """
        Retorna uma feature específica
        """
        try:
            # Tenta buscar do Redis primeiro
            redis_key = f"feature:{feature_id}"
            cached_feature = await self.redis.get(redis_key)
            
            if cached_feature:
                return Feature(**json.loads(cached_feature))
            
            # Se não encontrar no Redis, busca do MongoDB
            doc = await self.db.features.find_one({"_id": ObjectId(feature_id)})
            if doc:
                doc['id'] = str(doc.pop('_id'))
                feature = Feature(**doc)
                
                # Atualiza o cache
                await self.redis.set(redis_key, json.dumps(feature.model_dump(), cls=CustomEncoder))
                
                return feature
                
            return None
        except Exception as e:
            print(f"Error getting feature: {e}")
            raise

    async def create_feature_group(self, group: FeatureGroup) -> FeatureGroup:
        """
        Cria um novo grupo de features
        """
        try:
            # Salva no MongoDB
            group_dict = group.model_dump(exclude={'id'})
            result = await self.db.feature_groups.insert_one(group_dict)
            group.id = str(result.inserted_id)

            # Salva no Redis
            redis_key = f"feature_group:{group.id}"
            await self.redis.set(redis_key, json.dumps(group.model_dump(), cls=CustomEncoder))

            return group
        except Exception as e:
            print(f"Error creating feature group: {e}")
            raise

    async def list_feature_groups(self) -> List[dict]:
        """
        Lista todos os grupos de features
        """
        try:
            print("Iniciando busca de feature groups...")
            cursor = self.db.feature_groups.find()
            groups = []
            
            print("Iterando sobre os documentos...")
            async for doc in cursor:
                try:
                    print("Processando documento:", doc)
                    # Converter ObjectId para string
                    doc['id'] = str(doc.pop('_id'))
                    groups.append(doc)
                except Exception as e:
                    print(f"Error processing feature group: {e}")
                    continue
            
            print(f"Total de grupos encontrados: {len(groups)}")
            return groups
        except Exception as e:
            print(f"Error listing feature groups: {e}")
            raise

    async def get_feature_group(self, group_id: str) -> Optional[FeatureGroup]:
        """
        Retorna um grupo de features específico
        """
        try:
            # Tenta buscar do Redis primeiro
            redis_key = f"feature_group:{group_id}"
            cached_group = await self.redis.get(redis_key)
            
            if cached_group:
                return FeatureGroup(**json.loads(cached_group))
            
            # Se não encontrar no Redis, busca do MongoDB
            doc = await self.db.feature_groups.find_one({"_id": ObjectId(group_id)})
            if doc:
                doc['id'] = str(doc.pop('_id'))
                group = FeatureGroup(**doc)
                
                # Atualiza o cache
                await self.redis.set(redis_key, json.dumps(group.model_dump(), cls=CustomEncoder))
                
                return group
                
            return None
        except Exception as e:
            print(f"Error getting feature group: {e}")
            raise

    async def store_feature_value(self, feature_id: str, value: FeatureValue):
        """
        Armazena um valor de feature
        """
        try:
            # Salva no MongoDB
            value_dict = value.model_dump()
            value_dict['feature_id'] = ObjectId(feature_id)
            result = await self.db.feature_values.insert_one(value_dict)
            value_dict['_id'] = result.inserted_id

            # Atualiza o último valor no Redis
            redis_key = f"feature_value:{feature_id}:{value.entity_id}"
            await self.redis.set(redis_key, json.dumps(value_dict, cls=CustomEncoder))

            return value
        except Exception as e:
            print(f"Error storing feature value: {e}")
            raise

    async def get_feature_value(self, feature_id: str, entity_id: str) -> Optional[FeatureValue]:
        """
        Retorna o último valor de uma feature para uma entidade
        """
        try:
            # Tenta buscar do Redis primeiro
            redis_key = f"feature_value:{feature_id}:{entity_id}"
            cached_value = await self.redis.get(redis_key)
            
            if cached_value:
                return FeatureValue(**json.loads(cached_value))
            
            # Se não encontrar no Redis, busca do MongoDB
            doc = await self.db.feature_values.find_one(
                {"feature_id": ObjectId(feature_id), "entity_id": entity_id},
                sort=[("timestamp", -1)]
            )
            
            if doc:
                value = FeatureValue(**doc)
                
                # Atualiza o cache
                await self.redis.set(redis_key, json.dumps(doc, cls=CustomEncoder))
                
                return value
                
            return None
        except Exception as e:
            print(f"Error getting feature value: {e}")
            raise
