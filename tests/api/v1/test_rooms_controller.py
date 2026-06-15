import pytest
from unittest.mock import patch
from litestar.testing import TestClient
from litestar import Litestar
from uuid import uuid4

from app.api.v1.rooms_controller import RoomsController 
from app.domain.structs import RoomResponse
from litestar.datastructures import State
from unittest.mock import MagicMock

app_test = Litestar(
    route_handlers=[RoomsController],
    state=State({"http_client": MagicMock()}) 
)

@patch("app.api.v1.rooms_controller.rooms_service.proxy_get_room")
def test_controller_get_room(mock_proxy_get_room):
    room_id_str = str(uuid4())
    fake_room = RoomResponse(id=uuid4(), name="Test", capacity=5, creator_id=uuid4(), status="active", xp_multiplier=1.0, description=None)
    
    mock_proxy_get_room.return_value = fake_room

    with TestClient(app=app_test) as client:
        response = client.get(
            f"/rooms/{room_id_str}",
            headers={"Authorization": "Bearer el_token_secreto"}
        )

    assert response.status_code == 200
    assert response.json()["name"] == "Test"

    mock_proxy_get_room.assert_called_once()
    
    llamada_argumentos = mock_proxy_get_room.call_args.args
    
    assert llamada_argumentos[2] == "el_token_secreto"