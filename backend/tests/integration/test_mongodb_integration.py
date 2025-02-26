"""Testes de integração com MongoDB."""
import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

@pytest.mark.asyncio
async def test_mongodb_connection():
    """Testa conexão com MongoDB."""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB]
    
    # Testa conexão
    await db.command("ping")
    
    client.close()

@pytest.mark.asyncio
async def test_mongodb_crud():
    """Testa operações CRUD no MongoDB."""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB]
    collection = db.test_collection
    
    # Testa inserção
    document = {"name": "test", "value": 1}
    result = await collection.insert_one(document)
    assert result.inserted_id is not None
    
    # Testa leitura
    doc = await collection.find_one({"name": "test"})
    assert doc is not None
    assert doc["value"] == 1
    
    # Testa atualização
    result = await collection.update_one(
        {"name": "test"},
        {"$set": {"value": 2}}
    )
    assert result.modified_count == 1
    
    # Testa deleção
    result = await collection.delete_one({"name": "test"})
    assert result.deleted_count == 1
    
    client.close()

@pytest.mark.asyncio
async def test_mongodb_bulk_operations():
    """Testa operações em lote no MongoDB."""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB]
    collection = db.test_collection
    
    # Testa inserção em lote
    documents = [
        {"name": f"test{i}", "value": i}
        for i in range(10)
    ]
    result = await collection.insert_many(documents)
    assert len(result.inserted_ids) == 10
    
    # Testa atualização em lote
    result = await collection.update_many(
        {"value": {"$lt": 5}},
        {"$inc": {"value": 10}}
    )
    assert result.modified_count == 5
    
    # Testa deleção em lote
    result = await collection.delete_many({"name": {"$regex": "test"}})
    assert result.deleted_count == 10
    
    client.close()

@pytest.mark.asyncio
async def test_mongodb_index():
    """Testa operações com índices no MongoDB."""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB]
    collection = db.test_collection
    
    # Cria índice
    await collection.create_index("name")
    
    # Lista índices
    indices = await collection.list_indexes().to_list(None)
    assert len(indices) > 1  # _id index + nosso índice
    
    # Dropa índice
    await collection.drop_index("name_1")
    
    client.close()
