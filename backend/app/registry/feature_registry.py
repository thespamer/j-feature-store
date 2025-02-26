from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING

from app.core.config import settings
from app.core.exceptions import ValidationError, RegistryError
from app.models.feature import Feature, FeatureCreate
from app.registry.validation import validate_feature_definition

class FeatureRegistry:
    """Registro central de features."""
    
    def __init__(self, client: Optional[AsyncIOMotorClient] = None):
        """Inicializa o registro de features."""
        self.client = client
        if not self.client:
            self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        self.db = self.client.get_database(settings.MONGODB_DB)
        self.features = self.db.get_collection('features')
        self.lineage = self.db.get_collection('lineage')

    async def setup(self):
        """Configura o registro de features."""
        await self._setup_indexes()

    async def _setup_indexes(self):
        """Configura índices necessários."""
        await self.features.create_index([("name", ASCENDING), ("version", ASCENDING)], unique=True)
        await self.features.create_index([("tags", ASCENDING)])
        await self.lineage.create_index([("feature_id", ASCENDING), ("timestamp", DESCENDING)])

    async def register_feature(self, definition: Dict[str, Any]) -> str:
        """
        Registra uma nova feature.
        
        Args:
            definition: Definição da feature
            
        Returns:
            ID da feature registrada
        """
        # Validar definição
        if not validate_feature_definition(definition):
            raise ValidationError("Definição de feature inválida")
            
        # Verificar duplicatas
        existing = await self.features.find_one({
            "name": definition["name"],
            "version": definition.get("version", "1.0.0")
        })
        if existing:
            raise ValidationError(f"Feature {definition['name']} já existe")
            
        # Preparar documento
        feature_id = str(uuid.uuid4())
        feature_doc = {
            "id": feature_id,
            **definition,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "version": definition.get("version", "1.0.0"),
            "status": "active"
        }
        
        # Inserir no banco
        await self.features.insert_one(feature_doc)
        return feature_id

    async def update_feature(self, feature_id: str, updates: Dict[str, Any]) -> bool:
        """
        Atualiza uma feature existente.
        
        Args:
            feature_id: ID da feature
            updates: Atualizações a serem aplicadas
            
        Returns:
            True se atualizado com sucesso
        """
        # Verifica se feature existe
        feature = await self.get_feature(feature_id)
        
        # Incrementa versão
        current_version = feature.version.split(".")
        current_version[-1] = str(int(current_version[-1]) + 1)
        updates["version"] = ".".join(current_version)
        
        # Aplica atualizações
        result = await self.features.update_one(
            {"id": feature_id},
            {
                "$set": {
                    **updates,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0

    async def delete_feature(self, feature_id: str) -> bool:
        """
        Remove uma feature.
        
        Args:
            feature_id: ID da feature
            
        Returns:
            True se removida com sucesso
        """
        # Verifica se feature existe
        await self.get_feature(feature_id)
        
        # Remove feature
        result = await self.features.delete_one({"id": feature_id})
        return result.deleted_count > 0

    async def get_feature(self, feature_id: str) -> Feature:
        """
        Recupera uma feature pelo ID.
        
        Args:
            feature_id: ID da feature
            
        Returns:
            Objeto Feature
        """
        feature_doc = await self.features.find_one({"id": feature_id})
        if not feature_doc:
            raise ValidationError(f"Feature {feature_id} não encontrada")
        return Feature(**feature_doc)

    async def search_features(self, query: Dict[str, Any]) -> List[Feature]:
        """
        Busca features por critérios.
        
        Args:
            query: Critérios de busca
            
        Returns:
            Lista de features encontradas
        """
        cursor = self.features.find(query)
        features = []
        async for doc in cursor:
            features.append(Feature(**doc))
        return features

    async def get_feature_lineage(self, feature_id: str) -> List[Dict[str, Any]]:
        """
        Recupera o histórico de uma feature.
        
        Args:
            feature_id: ID da feature
            
        Returns:
            Lista de entradas de linhagem
        """
        cursor = self.lineage.find({"feature_id": feature_id}).sort("timestamp", DESCENDING)
        return [doc async for doc in cursor]

    async def add_lineage_entry(self, entry: Dict[str, Any]) -> str:
        """
        Adiciona uma entrada na linhagem.
        
        Args:
            entry: Entrada de linhagem
            
        Returns:
            ID da entrada
        """
        entry_id = str(uuid.uuid4())
        entry_doc = {
            "id": entry_id,
            **entry,
            "timestamp": entry.get("timestamp", datetime.utcnow())
        }
        await self.lineage.insert_one(entry_doc)
        return entry_id

    async def validate_feature_value(self, feature_id: str, value: Dict[str, Any]) -> bool:
        """
        Valida um valor de feature.
        
        Args:
            feature_id: ID da feature
            value: Valor a ser validado
            
        Returns:
            True se valor é válido
        """
        feature = await self.get_feature(feature_id)
        if not feature.validation_rules:
            return True
            
        rules = feature.validation_rules
        val = value["value"]
        
        if not rules.allow_null and val is None:
            raise ValidationError("Valor não pode ser nulo")
            
        if rules.min_value is not None and val < rules.min_value:
            raise ValidationError(f"Valor {val} é menor que o mínimo {rules.min_value}")
            
        if rules.max_value is not None and val > rules.max_value:
            raise ValidationError(f"Valor {val} é maior que o máximo {rules.max_value}")
            
        return True
