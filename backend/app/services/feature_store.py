from typing import List, Optional
from datetime import datetime
import json
import asyncio
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as redis
import asyncpg
from app.models.feature import Feature, FeatureValue
from app.models.feature_group import FeatureGroup
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
        self.postgres = None

    async def initialize(self):
        """Inicializa as conexões de forma assíncrona"""
        print("Conectando ao MongoDB...")
        # Inicializa MongoDB
        self.client = AsyncIOMotorClient("mongodb://mongodb:27017")
        print("Conexão estabelecida, selecionando banco de dados 'fstore'...")
        self.db = self.client.fstore

        print("Conectando ao Redis...")
        # Inicializa Redis
        self.redis = redis.Redis.from_url('redis://redis:6379/0')
        print("Conexão com Redis estabelecida com sucesso")

        print("Conectando ao PostgreSQL...")
        # Inicializa PostgreSQL com retry
        max_retries = 5
        retry_delay = 2
        for attempt in range(max_retries):
            try:
                self.postgres = await asyncpg.connect(
                    host="postgres",
                    database="fstore",
                    user="postgres",
                    password="postgres"
                )
                print("Conexão com PostgreSQL estabelecida com sucesso")
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"Failed to connect to PostgreSQL after {max_retries} attempts: {e}")
                    raise
                print(f"Failed to connect to PostgreSQL (attempt {attempt + 1}/{max_retries}): {e}")
                await asyncio.sleep(retry_delay)

    async def create_feature(self, feature: Feature) -> Feature:
        """
        Cria uma nova feature
        """
        try:
            # Salva no MongoDB
            feature_dict = feature.model_dump(exclude={'id'})
            result = await self.db.features.insert_one(feature_dict)
            feature.id = str(result.inserted_id)

            # Salva no PostgreSQL
            await self.postgres.execute("""
                INSERT INTO features (id, name, description)
                VALUES ($1, $2, $3)
            """, feature.id, feature.name, feature.description)

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
                feature_dict = json.loads(cached_feature)
                return Feature(**feature_dict)
            
            # Se não encontrou no Redis, busca no MongoDB
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
            # Salva no PostgreSQL
            await self.postgres.execute("""
                INSERT INTO feature_values (feature_id, entity_id, value, timestamp)
                VALUES ($1, $2, $3, $4)
            """, feature_id, value.entity_id, value.value, value.timestamp)

            # Atualiza o último valor no Redis
            redis_key = f"feature_value:{feature_id}:{value.entity_id}"
            await self.redis.set(redis_key, json.dumps(value.model_dump(), cls=CustomEncoder))

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
                try:
                    value_dict = json.loads(cached_value)
                    return FeatureValue(**value_dict)
                except Exception as e:
                    print(f"Error deserializing Redis value: {e}")
                    # Continue to PostgreSQL if Redis deserialization fails
            
            # Se não encontrou no Redis, busca do PostgreSQL
            row = await self.postgres.fetchrow("""
                SELECT feature_id, entity_id, value, timestamp
                FROM feature_values
                WHERE feature_id = $1 AND entity_id = $2
                ORDER BY timestamp DESC
                LIMIT 1
            """, feature_id, entity_id)
                
            if row:
                value = FeatureValue(
                    feature_id=row['feature_id'],
                    entity_id=row['entity_id'],
                    value=row['value'],
                    timestamp=row['timestamp']
                )
                
                # Atualiza o cache do Redis
                try:
                    await self.redis.set(
                        redis_key,
                        json.dumps(value.model_dump(), cls=CustomEncoder),
                        ex=3600  # Cache for 1 hour
                    )
                except Exception as e:
                    print(f"Error caching value in Redis: {e}")
                    # Continue even if Redis caching fails
                
                return value
            return None
        except Exception as e:
            print(f"Error getting feature value: {e}")
            raise

    async def get_feature_values(self, feature_id: str, entity_id: str) -> List[FeatureValue]:
        """
        Retorna os valores de uma feature para uma entidade
        """
        try:
            # Busca os valores no PostgreSQL
            rows = await self.postgres.fetch("""
                SELECT feature_id, entity_id, value, timestamp
                FROM feature_values
                WHERE feature_id = $1 AND entity_id = $2
                ORDER BY timestamp DESC
            """, feature_id, entity_id)
                
            values = []
            for row in rows:
                value = FeatureValue(
                    feature_id=row['feature_id'],
                    entity_id=row['entity_id'],
                    value=row['value'],
                    timestamp=row['timestamp']
                )
                values.append(value)
            return values
        except Exception as e:
            print(f"Error getting feature values: {e}")
            raise
