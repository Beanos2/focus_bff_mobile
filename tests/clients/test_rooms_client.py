import pytest
import httpx
import msgspec
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime

from app.clients.rooms_client import get_room
from app.domain.structs import RoomResponse

@pytest.mark.asyncio
async def test_get_room_success():
    
    fake_room_id = uuid4()
    fake_room = RoomResponse(
        id=fake_room_id, name="Sala de Estudio", capacity=5, 
        creator_id=uuid4(), status="active", xp_multiplier=1.5, description=None
    )
    
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    
    mock_response = MagicMock() 
    mock_response.raise_for_status.return_value = None
    mock_response.content = msgspec.json.encode(fake_room)
    
    mock_client.get.return_value = mock_response

    result = await get_room(mock_client, fake_room_id, "token_falso")

    assert result.id == fake_room_id
    assert result.name == "Sala de Estudio"
    assert result.xp_multiplier == 1.5
    mock_client.get.assert_called_once()