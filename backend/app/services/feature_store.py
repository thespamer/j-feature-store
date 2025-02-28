"""Serviço principal do Feature Store."""
from datetime import datetime
from typing import List, Optional, Dict, Any
import pandas as pd
from bson import ObjectId
import asyncpg

from app.models.feature import Feature, FeatureCreate, FeatureUpdate
from app.models.feature_group import FeatureGroup, FeatureGroupCreate, FeatureGroupUpdate
from app.core.config import settings
from app.core.validation import validate_feature_definition

class FeatureNotFoundError(Exception):
    pass

class FeatureStore:
    """Serviço para gerenciamento de features."""

    def __init__(self, mongodb_client, postgres_pool: asyncpg.Pool):
        """Inicializa o feature store."""
        self.db = mongodb_client
        self.postgres_pool = postgres_pool

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
        
        # Se a feature pertence a um grupo, atualiza o grupo
        if feature_data.feature_group_id:
            await self.db.feature_groups.update_one(
                {"_id": ObjectId(feature_data.feature_group_id)},
                {
                    "$addToSet": {"features": feature_dict["id"]},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
        
        return Feature(**feature_dict)

    async def get_feature(self, feature_id: str) -> Optional[Feature]:
        """Obtém uma feature pelo ID."""
        feature_data = await self.db.features.find_one({"_id": ObjectId(feature_id)})
        if feature_data:
            return Feature(**self._convert_mongodb_doc(feature_data))
        raise FeatureNotFoundError(f"Feature {feature_id} not found")

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
        # Primeiro busca a feature para saber seu grupo
        feature = await self.get_feature(feature_id)
        if feature and feature.feature_group_id:
            # Remove a feature do grupo
            await self.db.feature_groups.update_one(
                {"_id": ObjectId(feature.feature_group_id)},
                {
                    "$pull": {"features": feature_id},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
        
        # Remove a feature e seus valores
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
        raise FeatureNotFoundError(f"Feature group {group_id} not found")

    async def list_feature_groups(
        self,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        entity_type: Optional[str] = None,
        tag: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[FeatureGroup]:
        """Lista grupos de features com filtros opcionais."""
        query = {}
        if entity_type:
            query["entity_type"] = entity_type
        if tag:
            query["tags"] = tag
        if status:
            query["status"] = status

        cursor = self.db.feature_groups.find(query)
        if skip is not None:
            cursor = cursor.skip(skip)
        if limit is not None:
            cursor = cursor.limit(limit)

        groups = []
        async for doc in cursor:
            converted_doc = self._convert_mongodb_doc(doc)
            groups.append(FeatureGroup(**converted_doc))
        return groups

    async def update_feature_group(
        self,
        group_id: str,
        group_update: FeatureGroupUpdate
    ) -> Optional[FeatureGroup]:
        """Atualiza um grupo de features."""
        update_data = group_update.dict(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.utcnow()
            
            # Se estiver atualizando features, validar se elas existem
            if "features" in update_data:
                features = update_data["features"] or []
                for feature_id in features:
                    feature = await self.get_feature(feature_id)
                    if not feature:
                        raise ValueError(f"Feature {feature_id} não encontrada")

            result = await self.db.feature_groups.find_one_and_update(
                {"_id": ObjectId(group_id)},
                {"$set": update_data},
                return_document=True
            )
            if result:
                return FeatureGroup(**self._convert_mongodb_doc(result))
        return None

    async def get_features_by_group(self, group_id: str) -> List[Feature]:
        """Obtém todas as features de um grupo."""
        group = await self.get_feature_group(group_id)
        if not group:
            return []
        
        features = []
        for feature_id in group.features:
            feature = await self.get_feature(feature_id)
            if feature:
                features.append(feature)
        return features

    async def get_feature_group_statistics(self, group_id: str) -> Dict[str, Any]:
        """Obtém estatísticas agregadas do grupo de features."""
        features = await self.get_features_by_group(group_id)
        
        stats = {
            "total_features": len(features),
            "feature_types": {},
            "update_frequency": {},
            "last_updated": None,
            "completeness": 0.0,
            "quality_score": 0.0
        }

        for feature in features:
            # Contagem por tipo
            stats["feature_types"][feature.type] = stats["feature_types"].get(feature.type, 0) + 1
            
            # Última atualização
            if feature.updated_at:
                if not stats["last_updated"] or feature.updated_at > stats["last_updated"]:
                    stats["last_updated"] = feature.updated_at

            # Calcular qualidade e completude
            if feature.validation_rules:
                stats["quality_score"] += 1
            
        if features:
            stats["quality_score"] = (stats["quality_score"] / len(features)) * 100
            
        return stats

    async def delete_feature_group(self, group_id: str) -> None:
        """Remove um grupo de features."""
        await self.db.feature_groups.delete_one({"_id": ObjectId(group_id)})

    async def get_feature_values_as_of(
        self,
        feature_ids: List[str],
        entity_ids: List[str],
        timestamp: datetime
    ) -> pd.DataFrame:
        """
        Recupera valores das features para uma lista de entidades em um ponto específico no tempo.
        Implementa point-in-time correctness garantindo que só usamos dados disponíveis até o timestamp.
        """
        features_data = []
        
        for feature_id in feature_ids:
            # Obtém a feature
            feature = await self.get_feature(feature_id)
            if not feature:
                continue
                
            # Para cada entidade
            for entity_id in entity_ids:
                # Busca o último valor antes do timestamp
                value_doc = await self.db.feature_values.find_one(
                    {
                        "feature_id": feature_id,
                        "entity_id": entity_id,
                        "timestamp": {"$lte": timestamp}
                    },
                    sort=[("timestamp", -1)]
                )
                
                if value_doc:
                    features_data.append({
                        "feature_id": feature_id,
                        "feature_name": feature.name,
                        "entity_id": entity_id,
                        "value": value_doc["value"],
                        "timestamp": value_doc["timestamp"]
                    })
                
        # Converte para DataFrame
        if not features_data:
            return pd.DataFrame()
            
        df = pd.DataFrame(features_data)
        
        # Pivota para ter features como colunas
        df_pivot = df.pivot(
            index="entity_id",
            columns="feature_name",
            values="value"
        ).reset_index()
        
        return df_pivot

    async def get_training_dataset(
        self,
        feature_group_id: str,
        start_time: datetime,
        end_time: datetime,
        entity_df: pd.DataFrame,
        entity_id_column: str = "entity_id",
        timestamp_column: str = "timestamp"
    ) -> pd.DataFrame:
        """
        Cria um dataset de treinamento com point-in-time correctness.
        
        Args:
            feature_group_id: ID do grupo de features
            start_time: Data inicial para o dataset
            end_time: Data final para o dataset
            entity_df: DataFrame com IDs das entidades e timestamps
            entity_id_column: Nome da coluna com IDs das entidades
            timestamp_column: Nome da coluna com timestamps
        """
        # Obtém o grupo de features
        group = await self.get_feature_group(feature_group_id)
        if not group:
            raise ValueError(f"Feature group {feature_group_id} not found")
            
        # Inicializa DataFrame final
        final_df = entity_df.copy()
        
        # Para cada timestamp único no DataFrame de entidades
        for timestamp in entity_df[timestamp_column].unique():
            # Obtém entidades para este timestamp
            entities_at_time = entity_df[
                entity_df[timestamp_column] == timestamp
            ][entity_id_column].tolist()
            
            # Obtém valores das features para estas entidades neste ponto no tempo
            features_df = await self.get_feature_values_as_of(
                group.features,
                entities_at_time,
                timestamp
            )
            
            if not features_df.empty:
                # Merge com o DataFrame final
                final_df = pd.merge(
                    final_df,
                    features_df,
                    on=entity_id_column,
                    how="left"
                )
        
        return final_df

    async def insert_feature_value(
        self,
        feature_id: str,
        value_data: Dict[str, Any]
    ) -> None:
        """Insere um novo valor para uma feature."""
        value_doc = {
            "feature_id": feature_id,
            "value": value_data["value"],
            "timestamp": value_data.get("timestamp", datetime.utcnow()),
            "metadata": value_data.get("metadata", {})
        }
        
        if "entity_id" in value_data:
            value_doc["entity_id"] = value_data["entity_id"]
            
        await self.db.feature_values.insert_one(value_doc)

    async def get_feature_values(
        self,
        feature_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
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
            values.append(value_data)
        return values

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
            await self.db.command("ping")
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
            raise FeatureNotFoundError(f"Feature {feature_id} not found")

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
