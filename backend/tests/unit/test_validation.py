"""Testes para o módulo de validação."""
import pytest
from datetime import datetime

from app.registry.validation import (
    validate_feature_definition,
    validate_feature_value,
    validate_feature_group_definition
)
from app.core.exceptions import ValidationError
from app.models.feature import FeatureCreate

@pytest.fixture
def valid_feature():
    """Fixture para uma feature válida."""
    return FeatureCreate(
        name="test_feature",
        version="1.0.0",
        description="Test feature",
        type="numeric",
        entity_type="user",
        value_type="float",
        default_value=0.0,
        validation_rules={
            "min_value": 0,
            "max_value": 100,
            "allow_null": False
        },
        transformation={
            "type": "standard_scaler",
            "params": {}
        },
        metadata={
            "owner": "test_team",
            "created_at": datetime.utcnow().isoformat(),
            "tags": ["test", "numeric"]
        }
    )

@pytest.fixture
def valid_feature_group_definition():
    """Fixture para uma definição válida de grupo de features."""
    return {
        "name": "test_group",
        "version": "1.0.0",
        "description": "Test feature group",
        "entity_type": "user",
        "features": [
            FeatureCreate(
                name="feature1",
                type="numeric",
                description="First feature",
                value_type="float",
                default_value=0.0,
                validation_rules={
                    "min_value": 0,
                    "max_value": 100,
                    "allow_null": False
                }
            ),
            FeatureCreate(
                name="feature2",
                type="categorical",
                description="Second feature",
                value_type="string",
                default_value="unknown",
                validation_rules={
                    "categorical_values": ["A", "B", "C"],
                    "allow_null": False
                }
            )
        ],
        "metadata": {
            "owner": "test_team",
            "created_at": datetime.utcnow().isoformat(),
            "tags": ["test", "group"]
        }
    }

def test_validate_feature_definition_valid(valid_feature):
    """Testa validação de definição válida de feature."""
    # Não deve levantar exceção
    assert validate_feature_definition(valid_feature) is True

def test_validate_feature_definition_invalid_name():
    """Testa validação de nome inválido de feature."""
    feature_def = {
        "name": "Invalid Name!",  # Nome com caracteres inválidos
        "type": "numeric",
        "description": "Test feature"
    }
    
    with pytest.raises(ValidationError):
        validate_feature_definition(feature_def)

def test_validate_feature_definition_invalid_type():
    """Testa validação de tipo inválido de feature."""
    feature_def = {
        "name": "test_feature",
        "type": "invalid_type",  # Tipo não suportado
        "description": "Test feature"
    }
    
    with pytest.raises(ValidationError):
        validate_feature_definition(feature_def)

def test_validate_feature_definition_missing_required():
    """Testa validação de definição sem campos obrigatórios."""
    # Sem nome
    feature_def = {
        "type": "numeric",
        "description": "Test feature"
    }
    with pytest.raises(ValidationError):
        validate_feature_definition(feature_def)
    
    # Sem tipo
    feature_def = {
        "name": "test_feature",
        "description": "Test feature"
    }
    with pytest.raises(ValidationError):
        validate_feature_definition(feature_def)

def test_validate_feature_definition_invalid_validation_rules():
    """Testa validação de regras de validação inválidas."""
    feature_def = {
        "name": "test_feature",
        "type": "numeric",
        "description": "Test feature",
        "validation_rules": {
            "min_value": "invalid",  # Deve ser número
            "max_value": 100
        }
    }
    
    with pytest.raises(ValidationError):
        validate_feature_definition(feature_def)

def test_validate_feature_definition_invalid_transformation():
    """Testa validação de transformação inválida."""
    feature_def = {
        "name": "test_feature",
        "type": "numeric",
        "description": "Test feature",
        "transformation": {
            "type": "invalid_transform"  # Transformação não suportada
        }
    }
    
    with pytest.raises(ValidationError):
        validate_feature_definition(feature_def)

def test_validate_feature_value_numeric(valid_feature):
    """Testa validação de valor numérico."""
    # Valor válido
    value = {
        "entity_id": "user123",
        "value": 50.0,
        "timestamp": datetime.utcnow().isoformat()
    }
    assert validate_feature_value(value, valid_feature) is True
    
    # Valor inválido (menor que o mínimo)
    value["value"] = -1.0
    with pytest.raises(ValidationError):
        validate_feature_value(value, valid_feature)
    
    # Valor inválido (maior que o máximo)
    value["value"] = 101.0
    with pytest.raises(ValidationError):
        validate_feature_value(value, valid_feature)

def test_validate_feature_value_categorical():
    """Testa validação de valor categórico."""
    feature = FeatureCreate(
        name="test_feature",
        version="1.0.0",
        description="Test feature",
        type="categorical",
        entity_type="user",
        value_type="string",
        default_value="unknown",
        validation_rules={
            "categorical_values": ["A", "B", "C"],
            "allow_null": False
        },
        metadata={
            "owner": "test_team",
            "created_at": datetime.utcnow().isoformat(),
            "tags": ["test", "categorical"]
        }
    )

    # Valor válido
    value = {
        "entity_id": "user123",
        "value": "A",
        "timestamp": datetime.utcnow().isoformat()
    }
    assert validate_feature_value(value, feature) is True

    # Valor inválido (não está na lista)
    value["value"] = "D"
    with pytest.raises(ValidationError):
        validate_feature_value(value, feature)

    # Valor inválido (tipo errado)
    value["value"] = 123
    with pytest.raises(ValidationError):
        validate_feature_value(value, feature)

def test_validate_feature_value_temporal():
    """Testa validação de valor temporal."""
    feature = FeatureCreate(
        name="test_feature",
        version="1.0.0",
        description="Test feature",
        type="temporal",
        entity_type="user",
        value_type="timestamp",
        default_value=None,
        validation_rules={
            "min_date": "2025-01-01T00:00:00",
            "max_date": "2025-12-31T23:59:59",
            "allow_null": False
        },
        metadata={
            "owner": "test_team",
            "created_at": datetime.utcnow().isoformat(),
            "tags": ["test", "temporal"]
        }
    )

    # Valor válido
    value = {
        "entity_id": "user123",
        "value": "2025-06-15T12:00:00",
        "timestamp": datetime.utcnow().isoformat()
    }
    assert validate_feature_value(value, feature) is True

    # Valor inválido (antes do mínimo)
    value["value"] = "2024-12-31T23:59:59"
    with pytest.raises(ValidationError):
        validate_feature_value(value, feature)

    # Valor inválido (depois do máximo)
    value["value"] = "2026-01-01T00:00:00"
    with pytest.raises(ValidationError):
        validate_feature_value(value, feature)

    # Valor inválido (formato errado)
    value["value"] = "invalid_date"
    with pytest.raises(ValidationError):
        validate_feature_value(value, feature)

def test_validate_feature_value_missing_required():
    """Testa validação de valor sem campos obrigatórios."""
    feature = FeatureCreate(
        name="test_feature",
        version="1.0.0",
        description="Test feature",
        type="numeric",
        entity_type="user",
        value_type="float",
        default_value=0.0,
        validation_rules={
            "min_value": 0,
            "max_value": 100,
            "allow_null": False
        },
        metadata={
            "owner": "test_team",
            "created_at": datetime.utcnow().isoformat(),
            "tags": ["test", "numeric"]
        }
    )

    # Sem entity_id
    value = {
        "value": 50.0,
        "timestamp": datetime.utcnow().isoformat()
    }
    with pytest.raises(ValidationError):
        validate_feature_value(value, feature)

    # Sem valor
    value = {
        "entity_id": "user123",
        "timestamp": datetime.utcnow().isoformat()
    }
    with pytest.raises(ValidationError):
        validate_feature_value(value, feature)

    # Sem timestamp
    value = {
        "entity_id": "user123",
        "value": 50.0
    }
    with pytest.raises(ValidationError):
        validate_feature_value(value, feature)

def test_validate_feature_group_definition_valid(valid_feature_group_definition):
    """Testa validação de definição válida de grupo de features."""
    # Não deve levantar exceção
    assert validate_feature_group_definition(valid_feature_group_definition) is True

def test_validate_feature_group_definition_invalid_name():
    """Testa validação de nome inválido de grupo de features."""
    group_def = {
        "name": "Invalid Group!",  # Nome com caracteres inválidos
        "features": []
    }
    
    with pytest.raises(ValidationError):
        validate_feature_group_definition(group_def)

def test_validate_feature_group_definition_missing_required():
    """Testa validação de grupo sem campos obrigatórios."""
    # Sem nome
    group_def = {
        "features": []
    }
    with pytest.raises(ValidationError):
        validate_feature_group_definition(group_def)
    
    # Sem features
    group_def = {
        "name": "test_group"
    }
    with pytest.raises(ValidationError):
        validate_feature_group_definition(group_def)

def test_validate_feature_group_definition_invalid_features():
    """Testa validação de features inválidas no grupo."""
    group_def = {
        "name": "test_group",
        "features": [
            {
                "name": "Invalid Name!",  # Nome inválido
                "type": "numeric"
            }
        ]
    }
    
    with pytest.raises(ValidationError):
        validate_feature_group_definition(group_def)
    
    group_def["features"][0]["name"] = "valid_name"
    group_def["features"][0]["type"] = "invalid_type"  # Tipo inválido
    
    with pytest.raises(ValidationError):
        validate_feature_group_definition(group_def)

def test_validate_feature_group_definition_duplicate_features():
    """Testa validação de features duplicadas no grupo."""
    group_def = {
        "name": "test_group",
        "features": [
            {
                "name": "feature1",
                "type": "numeric"
            },
            {
                "name": "feature1",  # Nome duplicado
                "type": "numeric"
            }
        ]
    }
    
    with pytest.raises(ValidationError):
        validate_feature_group_definition(group_def)
