"""Testes para o módulo de banco de dados MongoDB."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.db.mongodb import get_database, close_database

@pytest.mark.asyncio
async def test_get_database():
    """Testa obtenção de conexão com o banco de dados."""
    with patch('app.db.mongodb.AsyncIOMotorClient') as mock_client:
        mock_db = AsyncMock()
        mock_client.return_value.__getitem__.return_value = mock_db
        
        # Primeira chamada - deve criar nova conexão
        db1 = await get_database()
        assert db1 == mock_db
        mock_client.assert_called_once()
        
        # Segunda chamada - deve reutilizar conexão existente
        db2 = await get_database()
        assert db2 == mock_db
        assert mock_client.call_count == 1  # Não deve criar nova conexão

@pytest.mark.asyncio
async def test_close_database():
    """Testa fechamento de conexão com o banco de dados."""
    with patch('app.db.mongodb._client', new=MagicMock()) as mock_client:
        # Fecha conexão
        await close_database()
        mock_client.close.assert_called_once()
        
        # Fecha novamente - não deve ter efeito
        await close_database()
        assert mock_client.close.call_count == 1
