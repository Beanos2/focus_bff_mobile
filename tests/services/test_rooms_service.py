import pytest
import httpx
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from litestar.exceptions import HTTPException

from app.services.rooms_service import proxy_get_room
from app.domain.structs import RoomResponse

@pytest.mark.asyncio
@patch("app.services.rooms_service.rooms_client.get_room")
async def test_proxy_get_room_success(mock_get_room):
    fake_room = RoomResponse(id=uuid4(), name="Test", capacity=5, creator_id=uuid4(), status="active", xp_multiplier=1.0, description=None)
    mock_get_room.return_value = fake_room
    
    client = AsyncMock()
    result = await proxy_get_room(client, fake_room.id, "token")
    
    assert result == fake_room
    mock_get_room.assert_called_once()

@pytest.mark.asyncio
@patch("app.services.rooms_service.rooms_client.get_room")
async def test_proxy_get_room_throws_503_when_offline(mock_get_room):
    mock_request = httpx.Request("GET", "url")
    mock_get_room.side_effect = httpx.RequestError("No connection", request=mock_request)
    
    client = AsyncMock()
    
    with pytest.raises(HTTPException) as exc:
        await proxy_get_room(client, uuid4(), "token")
    
    assert exc.value.status_code == 503
    assert "fuera de línea" in exc.value.detail