"""Módulo de validação de features."""
import re
from typing import Dict, Any, Optional, List, Union
from datetime import datetime

from app.models.feature import Feature, FeatureCreate, ValidationRules
from app.models.feature_group import FeatureGroup, FeatureGroupCreate
from app.core.exceptions import ValidationError

def validate_feature_definition(feature_def: Union[FeatureCreate, Dict[str, Any]]) -> bool:
    """Valida definição de feature."""
    try:
        # Convert dict to FeatureCreate if needed
        if isinstance(feature_def, dict):
            feature_def = FeatureCreate(**feature_def)
        
        # Valida nome da feature
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', feature_def.name):
            raise ValidationError(f"Nome de feature inválido: {feature_def.name}")
        
        # Valida tipo da feature
        valid_types = ['numeric', 'categorical', 'temporal']
        if feature_def.type not in valid_types:
            raise ValidationError(f"Tipo de feature inválido: {feature_def.type}")
        
        # Valida regras de validação
        if feature_def.validation_rules:
            rules = feature_def.validation_rules
            
            if feature_def.type == 'numeric':
                if rules.min_value is not None and rules.max_value is not None:
                    if rules.min_value >= rules.max_value:
                        raise ValidationError("min_value deve ser menor que max_value")
            
            elif feature_def.type == 'categorical':
                if rules.categorical_values:
                    if not isinstance(rules.categorical_values, list):
                        raise ValidationError("categorical_values deve ser uma lista")
                    if len(rules.categorical_values) == 0:
                        raise ValidationError("categorical_values não pode estar vazio")
            
            elif feature_def.type == 'temporal':
                if rules.min_date and rules.max_date:
                    if rules.min_date >= rules.max_date:
                        raise ValidationError("min_date deve ser menor que max_date")
        
        # Valida transformação
        if feature_def.transformation:
            transform = feature_def.transformation
            
            if feature_def.type == 'numeric':
                valid_transforms = ['standard_scaler', 'min_max_scaler', 'log_transform']
                if transform.type not in valid_transforms:
                    raise ValidationError(f"Transformação inválida para feature numérica: {transform.type}")
            
            elif feature_def.type == 'categorical':
                valid_transforms = ['one_hot', 'label_encoding']
                if transform.type not in valid_transforms:
                    raise ValidationError(f"Transformação inválida para feature categórica: {transform.type}")
            
            elif feature_def.type == 'temporal':
                valid_transforms = ['timestamp', 'date_parts']
                if transform.type not in valid_transforms:
                    raise ValidationError(f"Transformação inválida para feature temporal: {transform.type}")
        
        return True
    
    except (KeyError, TypeError, ValueError) as e:
        raise ValidationError(f"Erro de validação: {str(e)}")

def validate_feature_value(value: Dict[str, Any], feature: Union[Feature, FeatureCreate]) -> bool:
    """Valida valor de feature."""
    try:
        # Valida campos obrigatórios
        required_fields = ['entity_id', 'value', 'timestamp']
        for field in required_fields:
            if field not in value:
                raise ValidationError(f"Campo obrigatório ausente: {field}")
        
        # Valida tipo do valor
        if feature.type == 'numeric':
            if not isinstance(value['value'], (int, float)):
                raise ValidationError(f"Valor deve ser numérico, recebido: {type(value['value'])}")
            
            if feature.validation_rules:
                if feature.validation_rules.min_value is not None and value['value'] < feature.validation_rules.min_value:
                    raise ValidationError(f"Valor menor que o mínimo permitido: {value['value']} < {feature.validation_rules.min_value}")
                
                if feature.validation_rules.max_value is not None and value['value'] > feature.validation_rules.max_value:
                    raise ValidationError(f"Valor maior que o máximo permitido: {value['value']} > {feature.validation_rules.max_value}")
        
        elif feature.type == 'categorical':
            if not isinstance(value['value'], str):
                raise ValidationError(f"Valor deve ser string, recebido: {type(value['value'])}")
            
            if feature.validation_rules and feature.validation_rules.categorical_values:
                if value['value'] not in feature.validation_rules.categorical_values:
                    raise ValidationError(f"Valor não permitido: {value['value']}")
        
        elif feature.type == 'temporal':
            if not isinstance(value['value'], (str, datetime)):
                raise ValidationError(f"Valor deve ser string ISO ou datetime, recebido: {type(value['value'])}")
            
            try:
                if isinstance(value['value'], str):
                    value_date = datetime.fromisoformat(value['value'])
                else:
                    value_date = value['value']
                
                if feature.validation_rules:
                    if feature.validation_rules.min_date and value_date < feature.validation_rules.min_date:
                        raise ValidationError(f"Data anterior ao mínimo permitido: {value_date} < {feature.validation_rules.min_date}")
                    
                    if feature.validation_rules.max_date and value_date > feature.validation_rules.max_date:
                        raise ValidationError(f"Data posterior ao máximo permitido: {value_date} > {feature.validation_rules.max_date}")
            except ValueError as e:
                raise ValidationError(f"Formato de data inválido: {str(e)}")
        
        return True
    
    except (KeyError, TypeError, ValueError) as e:
        raise ValidationError(f"Erro de validação: {str(e)}")

def validate_feature_group_definition(group_def: Union[FeatureGroupCreate, Dict[str, Any]]) -> bool:
    """Valida definição de grupo de features."""
    try:
        # Convert dict to FeatureGroupCreate if needed
        if isinstance(group_def, dict):
            group_def = FeatureGroupCreate(**group_def)
        
        # Valida nome do grupo
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', group_def.name):
            raise ValidationError(f"Nome de grupo inválido: {group_def.name}")
        
        # Valida lista de features
        if not group_def.features:
            raise ValidationError("Lista de features vazia")
        
        # Verifica features duplicadas
        feature_names = [f.name for f in group_def.features]
        if len(feature_names) != len(set(feature_names)):
            raise ValidationError("Features duplicadas no grupo")
        
        # Valida cada feature do grupo
        for feature in group_def.features:
            validate_feature_definition(feature)
        
        return True
    
    except (KeyError, TypeError, ValueError) as e:
        raise ValidationError(f"Erro de validação: {str(e)}")
