"""Feature store service."""
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncpg
from motor.motor_asyncio import AsyncIOMotorClient
from redis.asyncio import Redis
from bson import ObjectId

from app.models.feature import Feature, FeatureValue, FeatureCreate
from app.models.feature_group import FeatureGroup, FeatureGroupCreate
from app.registry.validation import validate_feature_definition, validate_feature_value
from app.transformations.base import BaseTransformation
from app.transformations.numeric import NumericTransformation
from app.transformations.categorical import CategoricalTransformation
from app.transformations.temporal import TemporalTransformation
from app.core.config import settings
from app.core.exceptions import ValidationError

class FeatureNotFoundError(Exception):
    """Raised when a feature is not found."""
    pass

class FeatureStore:
    """Feature store service."""
    def __init__(self):
        """Initialize feature store."""
        print("Inicializando FeatureStore...")
        print("Conectando ao MongoDB em:", settings.MONGODB_URL)
        self.mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
        print("Conectando ao Redis em:", settings.REDIS_URL)
        self.redis_client = Redis.from_url(settings.REDIS_URL)
        self.postgres_pool = None
        print("Selecionando database:", settings.MONGODB_DB)
        self.db = self.mongo_client[settings.MONGODB_DB]
        print("FeatureStore inicializado com sucesso!")

    async def initialize(self):
        """Initialize feature store connections."""
        self.postgres_pool = await asyncpg.create_pool(
            settings.POSTGRES_URL,
            min_size=5,
            max_size=10
        )

    def _convert_mongodb_doc(self, doc: Dict) -> Dict:
        """Converte um documento do MongoDB para um dicionário compatível com os modelos."""
        if doc is None:
            return None
        doc_dict = dict(doc)
        if "_id" in doc_dict:
            doc_dict["id"] = str(doc_dict["_id"])
            del doc_dict["_id"]
        # Converter ObjectId para string em campos aninhados
        for key, value in doc_dict.items():
            if isinstance(value, ObjectId):
                doc_dict[key] = str(value)
            elif isinstance(value, list):
                doc_dict[key] = [
                    str(item) if isinstance(item, ObjectId)
                    else self._convert_mongodb_doc(item) if isinstance(item, dict)
                    else item
                    for item in value
                ]
            elif isinstance(value, dict):
                doc_dict[key] = self._convert_mongodb_doc(value)
        return doc_dict

    async def create_feature(self, feature_data: FeatureCreate) -> Feature:
        """Cria uma nova feature."""
        validate_feature_definition(feature_data.dict())
        
        metadata = {
            "owner": "system",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        if feature_data.metadata:
            metadata.update(feature_data.metadata)

        # Primeiro insere no MongoDB para obter o ID
        feature_dict = {
            "name": feature_data.name,
            "type": feature_data.type,
            "description": feature_data.description,
            "metadata": metadata,
            "validation_rules": feature_data.validation_rules.dict() if feature_data.validation_rules else None,
            "transformation": feature_data.transformation.dict() if feature_data.transformation else None,
            "dependencies": feature_data.dependencies,
            "version": feature_data.version,
            "entity_id": feature_data.entity_id,
            "feature_group_id": feature_data.feature_group_id
        }
        
        result = await self.db.features.insert_one(feature_dict)
        feature_dict["id"] = str(result.inserted_id)
        
        # Atualiza a lista de features no grupo
        if feature_data.feature_group_id:
            await self.db.feature_groups.update_one(
                {"_id": ObjectId(feature_data.feature_group_id)},
                {"$addToSet": {"features": feature_dict["id"]}}
            )
        
        # Agora cria o objeto Feature com o ID
        return Feature(**feature_dict)

    async def get_feature(self, feature_id: str) -> Optional[Feature]:
        """Obtém uma feature pelo ID."""
        feature_data = await self.db.features.find_one({"_id": ObjectId(feature_id)})
        if feature_data:
            return Feature(**self._convert_mongodb_doc(feature_data))
        return None

    async def list_features(self) -> List[Feature]:
        """Lista todas as features."""
        features = []
        print("Tentando conectar ao MongoDB...")
        try:
            print("URL do MongoDB:", settings.MONGODB_URL)
            print("Database:", settings.MONGODB_DB)
            print("Iniciando busca de features...")
            async for feature_data in self.db.features.find():
                print("Feature encontrada:", feature_data)
                converted_data = self._convert_mongodb_doc(feature_data)
                print("Feature convertida:", converted_data)
                features.append(Feature(**converted_data))
            print("Total de features encontradas:", len(features))
            return features
        except Exception as e:
            print("Erro ao listar features:", str(e))
            raise

    async def delete_feature(self, feature_id: str) -> None:
        """Remove uma feature."""
        await self.db.features.delete_one({"_id": ObjectId(feature_id)})
        await self.db.feature_values.delete_many({"feature_id": feature_id})

    async def create_feature_group(self, group_data: FeatureGroupCreate) -> FeatureGroup:
        """Cria um novo grupo de features."""
        metadata = {
            "owner": "system",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        if group_data.metadata:
            metadata.update(group_data.metadata)

        group_dict = {
            "name": group_data.name,
            "description": group_data.description,
            "entity_type": group_data.entity_type,
            "features": group_data.features,
            "metadata": metadata,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "version": 1
        }
        
        result = await self.db.feature_groups.insert_one(group_dict)
        group_dict["id"] = str(result.inserted_id)
        
        return FeatureGroup(**group_dict)

    async def get_feature_group(self, group_id: str) -> Optional[FeatureGroup]:
        """Obtém um grupo de features pelo ID."""
        group_data = await self.db.feature_groups.find_one({"_id": ObjectId(group_id)})
        if group_data:
            return FeatureGroup(**self._convert_mongodb_doc(group_data))
        return None

    async def list_feature_groups(self) -> List[FeatureGroup]:
        """Lista todos os grupos de features."""
        try:
            groups = []
            async for group_data in self.db.feature_groups.find():
                converted_data = self._convert_mongodb_doc(group_data)
                groups.append(FeatureGroup(**converted_data))
            return groups
        except Exception as e:
            print("Erro ao listar grupos de features:", str(e))
            raise

    async def delete_feature_group(self, group_id: str) -> None:
        """Remove um grupo de features."""
        await self.db.feature_groups.delete_one({"_id": ObjectId(group_id)})

    async def insert_feature_value(self, feature_id: str, value: FeatureValue) -> FeatureValue:
        """Insere um valor para uma feature."""
        feature = await self.get_feature(feature_id)
        if not feature:
            raise FeatureNotFoundError("Feature não encontrada")

        validate_feature_value(feature, value.value)
        
        if feature.transformation:
            transformer = self._get_transformer(feature)
            value.value = transformer.transform(value.value)

        await self.db.feature_values.insert_one(value.dict())
        return value

    async def get_feature_values(
        self,
        feature_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[FeatureValue]:
        """Obtém valores de uma feature."""
        query = {"feature_id": feature_id}
        if start_time or end_time:
            query["timestamp"] = {}
            if start_time:
                query["timestamp"]["$gte"] = start_time
            if end_time:
                query["timestamp"]["$lte"] = end_time

        values = []
        async for value_data in self.db.feature_values.find(query):
            values.append(FeatureValue(**value_data))
        return values

    def _get_transformer(self, feature: Feature) -> BaseTransformation:
        """Obtém o transformador apropriado para a feature."""
        if feature.type == "numeric":
            return NumericTransformation()
        elif feature.type == "categorical":
            return CategoricalTransformation()
        elif feature.type == "temporal":
            return TemporalTransformation()
        else:
            raise ValueError(f"Tipo de feature inválido: {feature.type}")

    async def count_features(self) -> int:
        """Conta o número total de features."""
        return await self.db.features.count_documents({})

    async def count_feature_groups(self) -> int:
        """Conta o número total de grupos de features."""
        return await self.db.feature_groups.count_documents({})

    async def count_feature_values(self) -> int:
        """Conta o número total de valores de features."""
        return await self.db.feature_values.count_documents({})

    async def get_storage_usage(self) -> Dict[str, int]:
        """Obtém o uso de armazenamento."""
        stats = await self.db.command("dbStats")
        return {
            "data_size": stats["dataSize"],
            "storage_size": stats["storageSize"],
            "index_size": stats["indexSize"]
        }

    async def get_last_update_time(self) -> datetime:
        """Obtém o horário da última atualização."""
        latest = await self.db.feature_values.find_one(
            sort=[("timestamp", -1)]
        )
        return latest["timestamp"] if latest else datetime.min

    async def check_health(self) -> bool:
        """Verifica a saúde do sistema."""
        try:
            await self.mongo_client.admin.command("ping")
            self.redis_client.ping()
            return True
        except:
            return False

    async def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Obtém alertas ativos."""
        alerts = []
        async for alert in self.db.alerts.find({"status": "active"}):
            alerts.append(alert)
        return alerts

    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Obtém métricas de performance."""
        return {
            "latency": await self._get_average_latency(),
            "throughput": await self._get_throughput(),
            "error_rate": await self._get_error_rate()
        }

    async def get_feature_statistics(self, feature_id: str) -> Optional[Dict[str, Any]]:
        """Obtém estatísticas de uma feature."""
        feature = await self.get_feature(feature_id)
        if not feature:
            return None

        pipeline = [
            {"$match": {"feature_id": feature_id}},
            {"$group": {
                "_id": None,
                "count": {"$sum": 1},
                "avg": {"$avg": "$value"},
                "min": {"$min": "$value"},
                "max": {"$max": "$value"}
            }}
        ]
        
        result = await self.db.feature_values.aggregate(pipeline).to_list(1)
        if not result:
            return {"count": 0}
        
        stats = result[0]
        stats.pop("_id")
        return stats

    async def _get_average_latency(self) -> float:
        """Obtém a latência média das operações."""
        pipeline = [
            {"$match": {"type": "latency"}},
            {"$group": {"_id": None, "avg": {"$avg": "$value"}}}
        ]
        result = await self.db.metrics.aggregate(pipeline).to_list(1)
        return result[0]["avg"] if result else 0.0

    async def _get_throughput(self) -> float:
        """Obtém o throughput do sistema."""
        pipeline = [
            {"$match": {"type": "throughput"}},
            {"$group": {"_id": None, "sum": {"$sum": "$value"}}}
        ]
        result = await self.db.metrics.aggregate(pipeline).to_list(1)
        return result[0]["sum"] if result else 0.0

    async def _get_error_rate(self) -> float:
        """Obtém a taxa de erro do sistema."""
        total = await self.db.metrics.count_documents({"type": "request"})
        if not total:
            return 0.0
        errors = await self.db.metrics.count_documents({"type": "error"})
        return errors / total if total > 0 else 0.0
