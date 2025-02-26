"""Testes para o módulo de feature."""
import pytest
from datetime import datetime
from typing import Dict, Any

from app.models.feature import Feature, FeatureCreate, FeatureUpdate, FeatureValue, TransformationConfig, ValidationRules
from app.core.exceptions import ValidationError

@pytest.fixture
def valid_feature_data() -> Dict[str, Any]:
    """Fixture com dados válidos de feature."""
    return {
        "name": "test_feature",
        "type": "numeric",
        "description": "Test feature",
        "validation_rules": {
            "min_value": 0,
            "max_value": 100,
            "allow_null": False
        },
        "transformation": {
            "type": "standard_scaler"
        },
        "metadata": {
            "owner": "test_team",
            "tags": ["test", "numeric"]
        }
    }

@pytest.fixture
def valid_feature_value_data() -> Dict[str, Any]:
    """Fixture com dados válidos de valor de feature."""
    return {
        "feature_id": "test_feature",
        "value": 42,
        "timestamp": datetime.utcnow(),
        "metadata": {
            "source": "test",
            "confidence": 0.95
        }
    }

def test_feature_metadata():
    """Testa criação de metadados de feature."""
    metadata = {
        "owner": "test_team",
        "tags": ["test", "numeric"],
        "description": "Test feature"
    }
    
    feature = Feature(
        name="test_feature",
        type="numeric",
        metadata=metadata,
        created_at=datetime.utcnow()
    )
    
    assert feature.metadata == metadata
    assert "owner" in feature.metadata
    assert "tags" in feature.metadata
    assert "description" in feature.metadata

def test_transformation_config():
    """Testa configuração de transformação."""
    config = TransformationConfig(
        type="standard_scaler",
        params={"with_mean": True, "with_std": True}
    )
    
    assert config.type == "standard_scaler"
    assert config.params["with_mean"] is True
    assert config.params["with_std"] is True

def test_validation_rules():
    """Testa regras de validação."""
    rules = ValidationRules(
        min_value=0,
        max_value=100,
        allow_null=False
    )
    
    assert rules.min_value == 0
    assert rules.max_value == 100
    assert rules.allow_null is False

def test_feature_creation():
    """Testa criação de feature."""
    feature = Feature(
        name="test_feature",
        type="numeric",
        description="Test feature",
        validation_rules=ValidationRules(
            min_value=0,
            max_value=100,
            allow_null=False
        ),
        transformation=TransformationConfig(
            type="standard_scaler"
        ),
        metadata={
            "owner": "test_team",
            "tags": ["test", "numeric"]
        },
        created_at=datetime.utcnow()
    )
    
    assert feature.name == "test_feature"
    assert feature.type == "numeric"
    assert feature.description == "Test feature"
    assert feature.validation_rules.min_value == 0
    assert feature.validation_rules.max_value == 100
    assert feature.validation_rules.allow_null is False
    assert feature.transformation.type == "standard_scaler"
    assert "owner" in feature.metadata
    assert "tags" in feature.metadata

def test_feature_validation():
    """Testa validação de feature."""
    feature = Feature(
        name="test_feature",
        type="numeric",
        validation_rules=ValidationRules(
            min_value=0,
            max_value=100,
            allow_null=False
        ),
        created_at=datetime.utcnow()
    )
    
    assert feature.validation_rules.min_value == 0
    assert feature.validation_rules.max_value == 100
    assert feature.validation_rules.allow_null is False

def test_feature_versioning():
    """Testa versionamento de feature."""
    feature = Feature(
        name="test_feature",
        type="numeric",
        version=1,
        created_at=datetime.utcnow()
    )
    
    assert feature.version == 1

def test_feature_dependencies():
    """Testa dependências de feature."""
    feature = Feature(
        name="test_feature",
        type="numeric",
        dependencies=["feature1", "feature2"],
        created_at=datetime.utcnow()
    )
    
    assert len(feature.dependencies) == 2
    assert "feature1" in feature.dependencies
    assert "feature2" in feature.dependencies

def test_feature_metadata_updates():
    """Testa atualização de metadados."""
    feature = Feature(
        name="test_feature",
        type="numeric",
        metadata={
            "owner": "test_team",
            "tags": ["test"]
        },
        created_at=datetime.utcnow()
    )
    
    # Atualiza metadados
    feature.metadata["tags"].append("numeric")
    feature.metadata["description"] = "Test feature"
    
    assert "numeric" in feature.metadata["tags"]
    assert feature.metadata["description"] == "Test feature"

def test_feature_validation_rules_updates():
    """Testa atualização de regras de validação."""
    feature = Feature(
        name="test_feature",
        type="numeric",
        validation_rules=ValidationRules(
            min_value=0,
            max_value=100
        ),
        created_at=datetime.utcnow()
    )
    
    # Atualiza regras
    feature.validation_rules.allow_null = False
    
    assert feature.validation_rules.allow_null is False

def test_feature_transformation_updates():
    """Testa atualização de transformação."""
    feature = Feature(
        name="test_feature",
        type="numeric",
        transformation=TransformationConfig(
            type="standard_scaler"
        ),
        created_at=datetime.utcnow()
    )
    
    # Atualiza transformação
    feature.transformation.params = {"with_mean": True}
    
    assert feature.transformation.params["with_mean"] is True

def test_feature_create():
    """Testa modelo de criação de feature."""
    feature_create = FeatureCreate(
        name="test_feature",
        type="numeric",
        description="Test feature",
        validation_rules=ValidationRules(
            min_value=0,
            max_value=100
        ),
        transformation=TransformationConfig(
            type="standard_scaler"
        ),
        metadata={
            "owner": "test_team",
            "tags": ["test"]
        }
    )
    
    assert feature_create.name == "test_feature"
    assert feature_create.type == "numeric"
    assert feature_create.description == "Test feature"
    assert feature_create.validation_rules.min_value == 0
    assert feature_create.validation_rules.max_value == 100
    assert feature_create.transformation.type == "standard_scaler"
    assert "owner" in feature_create.metadata
    assert "tags" in feature_create.metadata

def test_feature_value():
    """Testa modelo de valor de feature."""
    feature_value = FeatureValue(
        feature_id="test_feature",
        value=42,
        timestamp=datetime.utcnow(),
        metadata={
            "source": "test",
            "confidence": 0.95
        }
    )
    
    assert feature_value.feature_id == "test_feature"
    assert feature_value.value == 42
    assert isinstance(feature_value.timestamp, datetime)
    assert feature_value.metadata["source"] == "test"
    assert feature_value.metadata["confidence"] == 0.95

def test_feature_create_model():
    """Testa modelo de criação de feature."""
    feature_create = FeatureCreate(
        name="test_feature",
        type="numeric",
        description="Test feature",
        validation_rules=ValidationRules(
            min_value=0,
            max_value=100,
            allow_null=False
        ),
        transformation=TransformationConfig(
            type="standard_scaler",
            params={"with_mean": True}
        ),
        metadata={
            "owner": "test_team",
            "tags": ["test", "numeric"]
        },
        dependencies=["feature1", "feature2"]
    )
    
    # Cria feature a partir do modelo de criação
    feature = Feature(
        **feature_create.model_dump(),
        created_at=datetime.utcnow()
    )
    
    assert feature.name == feature_create.name
    assert feature.type == feature_create.type
    assert feature.description == feature_create.description
    assert feature.validation_rules.min_value == feature_create.validation_rules.min_value
    assert feature.validation_rules.max_value == feature_create.validation_rules.max_value
    assert feature.validation_rules.allow_null == feature_create.validation_rules.allow_null
    assert feature.transformation.type == feature_create.transformation.type
    assert feature.transformation.params == feature_create.transformation.params
    assert feature.metadata == feature_create.metadata
    assert feature.dependencies == feature_create.dependencies
