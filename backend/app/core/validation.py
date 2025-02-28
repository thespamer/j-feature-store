from typing import Dict, Any
from app.models.feature import Feature

def validate_feature_definition(feature_def: Dict[str, Any]) -> None:
    """
    Validates a feature definition.
    
    Args:
        feature_def: Dictionary containing feature definition
        
    Raises:
        ValidationError: If the feature definition is invalid
    """
    required_fields = ['name', 'type']
    for field in required_fields:
        if field not in feature_def:
            raise ValidationError(f"Missing required field: {field}")
            
    valid_types = ['string', 'integer', 'float', 'boolean', 'timestamp']
    if feature_def['type'] not in valid_types:
        raise ValidationError(f"Invalid feature type. Must be one of: {', '.join(valid_types)}")

class ValidationError(Exception):
    pass
