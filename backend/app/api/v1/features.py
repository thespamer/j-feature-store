from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
from app.models.feature import Feature

router = APIRouter()

@router.get("/")
async def get_features() -> List[Feature]:
    """
    Retorna todas as features
    """
    try:
        features = [
            {
                "id": "1",
                "name": "idade_cliente",
                "description": "Idade do cliente em anos",
                "data_type": "float",
                "entity_id": "cliente_1",
                "feature_group_id": "1",
                "tags": ["cliente", "demográfico"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "metadata": {}
            },
            {
                "id": "2",
                "name": "categoria_produto",
                "description": "Categoria do produto",
                "data_type": "string",
                "entity_id": "produto_1",
                "feature_group_id": "2",
                "tags": ["produto", "catálogo"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "metadata": {}
            },
            {
                "id": "3",
                "name": "ultima_compra",
                "description": "Data da última compra",
                "data_type": "string",
                "entity_id": "cliente_1",
                "feature_group_id": "1",
                "tags": ["cliente", "transação"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "metadata": {}
            }
        ]
        return features
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_feature(feature: Feature):
    """
    Cria uma nova feature
    """
    try:
        # Aqui você implementaria a lógica de persistência
        return feature
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
