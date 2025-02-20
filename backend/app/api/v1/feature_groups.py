from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
from app.models.feature import FeatureGroup

router = APIRouter()

@router.get("/")
async def get_feature_groups() -> List[FeatureGroup]:
    """
    Retorna todos os grupos de features
    """
    try:
        groups = [
            {
                "id": "1",
                "name": "dados_cliente",
                "description": "Dados demográficos do cliente",
                "entity_type": "cliente",
                "features": ["idade_cliente", "ultima_compra"],
                "tags": ["cliente", "demográfico"],
                "frequency": "daily",
                "created_at": datetime.utcnow(),
                "metadata": {}
            },
            {
                "id": "2",
                "name": "dados_produto",
                "description": "Informações sobre produtos",
                "entity_type": "produto",
                "features": ["categoria_produto"],
                "tags": ["produto", "catálogo"],
                "frequency": "hourly",
                "created_at": datetime.utcnow(),
                "metadata": {}
            },
            {
                "id": "3",
                "name": "métricas_vendas",
                "description": "Métricas de vendas mensais",
                "entity_type": "venda",
                "features": [],
                "tags": ["venda", "financeiro"],
                "frequency": "monthly",
                "created_at": datetime.utcnow(),
                "metadata": {}
            }
        ]
        return groups
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_feature_group(group: FeatureGroup):
    """
    Cria um novo grupo de features
    """
    try:
        # Aqui você implementaria a lógica de persistência
        return group
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
