"""Testes para o registro de features."""
import pytest
import asyncio
import pytest_asyncio
from datetime import datetime
from typing import Dict, Any, AsyncGenerator
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.registry.feature_registry import FeatureRegistry
from app.models.feature import Feature, FeatureValue
from app.core.exceptions import ValidationError

@pytest_asyncio.fixture(scope="function")
async def feature_registry():
    """Fixture para o registro de features."""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    registry = FeatureRegistry(client)
    
    # Limpa coleções antes dos testes
    await registry.features.delete_many({})
    await registry.lineage.delete_many({})
    
    # Configura índices
    await registry.setup()
    
    yield registry
    
    # Limpa coleções após os testes
    await registry.features.delete_many({})
    await registry.lineage.delete_many({})
    client.close()  # Motor client doesn't need await for close

@pytest.fixture
def valid_feature_definition() -> Dict[str, Any]:
    """Feature válida para testes."""
    return {
        "name": "test_feature",
        "type": "numeric",
        "description": "Test feature",
        "metadata": {
            "owner": "test_team",
            "tags": ["test", "numeric"]
        },
        "transformation": {
            "type": "standard_scaler"
        }
    }

@pytest.mark.asyncio
async def test_register_feature(feature_registry: FeatureRegistry, valid_feature_definition: Dict[str, Any]):
    """Testa registro de feature."""
    # Registra feature
    feature_id = await feature_registry.register_feature(valid_feature_definition)
    assert feature_id is not None
    
    # Verifica se feature foi registrada
    feature = await feature_registry.get_feature(feature_id)
    assert feature.name == valid_feature_definition["name"]
    assert feature.type == valid_feature_definition["type"]
    assert feature.description == valid_feature_definition["description"]

@pytest.mark.asyncio
async def test_register_duplicate_feature(feature_registry: FeatureRegistry, valid_feature_definition: Dict[str, Any]):
    """Testa registro de feature duplicada."""
    # Registra feature
    await feature_registry.register_feature(valid_feature_definition)
    
    # Tenta registrar feature duplicada
    with pytest.raises(ValidationError):
        await feature_registry.register_feature(valid_feature_definition)

@pytest.mark.asyncio
async def test_update_feature(feature_registry: FeatureRegistry, valid_feature_definition: Dict[str, Any]):
    """Testa atualização de feature."""
    # Registra feature
    feature_id = await feature_registry.register_feature(valid_feature_definition)
    
    # Atualiza feature
    updates = {
        "description": "Updated description",
        "metadata": {
            "owner": "new_team",
            "tags": ["test", "updated"]
        }
    }
    success = await feature_registry.update_feature(feature_id, updates)
    assert success
    
    # Verifica se feature foi atualizada
    feature = await feature_registry.get_feature(feature_id)
    assert feature.description == updates["description"]
    assert feature.metadata == updates["metadata"]
    assert feature.version == "1.0.1"

@pytest.mark.asyncio
async def test_delete_feature(feature_registry: FeatureRegistry, valid_feature_definition: Dict[str, Any]):
    """Testa remoção de feature."""
    # Registra feature
    feature_id = await feature_registry.register_feature(valid_feature_definition)
    
    # Remove feature
    success = await feature_registry.delete_feature(feature_id)
    assert success
    
    # Verifica se feature foi removida
    with pytest.raises(ValidationError):
        await feature_registry.get_feature(feature_id)

@pytest.mark.asyncio
async def test_version_control(feature_registry: FeatureRegistry, valid_feature_definition: Dict[str, Any]):
    """Testa controle de versão."""
    # Registra feature
    feature_id = await feature_registry.register_feature(valid_feature_definition)
    
    # Verifica versão inicial
    feature = await feature_registry.get_feature(feature_id)
    assert feature.version == "1.0.0"
    
    # Atualiza feature
    await feature_registry.update_feature(feature_id, {"description": "Updated"})
    
    # Verifica nova versão
    feature = await feature_registry.get_feature(feature_id)
    assert feature.version == "1.0.1"

@pytest.mark.asyncio
async def test_feature_search(feature_registry: FeatureRegistry, valid_feature_definition: Dict[str, Any]):
    """Testa busca de features."""
    # Registra feature
    await feature_registry.register_feature(valid_feature_definition)
    
    # Busca features
    features = await feature_registry.search_features({"type": "numeric"})
    assert len(features) == 1
    assert features[0].type == "numeric"

@pytest.mark.asyncio
async def test_feature_validation(feature_registry: FeatureRegistry):
    """Testa validação de feature."""
    # Feature inválida
    invalid_feature = {
        "name": "123invalid",  # Nome inválido
        "type": "unknown",     # Tipo inválido
        "description": "Test"
    }
    
    # Tenta registrar feature inválida
    with pytest.raises(ValidationError):
        await feature_registry.register_feature(invalid_feature)

@pytest.mark.asyncio
async def test_feature_dependencies(feature_registry: FeatureRegistry, valid_feature_definition: Dict[str, Any]):
    """Testa dependências de feature."""
    # Registra primeira feature
    feature_id = await feature_registry.register_feature(valid_feature_definition)
    
    # Registra segunda feature com dependência
    dependent_feature = {
        **valid_feature_definition,
        "name": "dependent_feature",
        "dependencies": [feature_id]
    }
    dependent_id = await feature_registry.register_feature(dependent_feature)
    
    # Verifica dependência
    feature = await feature_registry.get_feature(dependent_id)
    assert feature_id in feature.dependencies

@pytest.mark.asyncio
async def test_feature_lineage(feature_registry: FeatureRegistry, valid_feature_definition: Dict[str, Any]):
    """Testa linhagem de feature."""
    # Registra feature
    feature_id = await feature_registry.register_feature(valid_feature_definition)
    
    # Adiciona entrada na linhagem
    entry = {
        "feature_id": feature_id,
        "event_type": "update",
        "details": {
            "field": "description",
            "old_value": "Test feature",
            "new_value": "Updated feature"
        }
    }
    entry_id = await feature_registry.add_lineage_entry(entry)
    assert entry_id is not None
    
    # Verifica linhagem
    lineage = await feature_registry.get_feature_lineage(feature_id)
    assert len(lineage) == 1
    assert lineage[0]["event_type"] == "update"

@pytest.mark.asyncio
async def test_feature_value_validation(feature_registry: FeatureRegistry, valid_feature_definition: Dict[str, Any]):
    """Testa validação de valor de feature."""
    # Registra feature com regras de validação
    feature_def = {
        **valid_feature_definition,
        "validation_rules": {
            "allow_null": False,
            "min_value": 0,
            "max_value": 100
        }
    }
    feature_id = await feature_registry.register_feature(feature_def)
    
    # Testa valor válido
    valid_value = {"value": 50}
    assert await feature_registry.validate_feature_value(feature_id, valid_value)
    
    # Testa valor inválido (nulo)
    with pytest.raises(ValidationError):
        await feature_registry.validate_feature_value(feature_id, {"value": None})
    
    # Testa valor inválido (fora do intervalo)
    with pytest.raises(ValidationError):
        await feature_registry.validate_feature_value(feature_id, {"value": 150})
