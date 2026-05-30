import os
import pytest
import respx
import jwt
from datetime import datetime, timedelta, timezone
from httpx import Response

os.environ["SECRET_KEY"] = "clave_super_secreta"
os.environ["AUTH_SERVICE_URL"] = "http://127.0.0.1:8001"
os.environ["STATS_SERVICE_URL"] = "http://127.0.0.1:8002"
os.environ["INVENTORY_SERVICE_URL"] = "http://127.0.0.1:8003"

from litestar.testing import TestClient
from app.main import app
from app.domain.structs import SyncPayload, SessionItem

app.debug = True

def get_test_token() -> str:
    secret = os.getenv("SECRET_KEY", "tu_clave_super_secreta")
    now = datetime.now(timezone.utc)
    token_payload = {
        "sub": "123e4567-e89b-12d3-a456-426614174000",
        "exp": now + timedelta(minutes=10),
        "iat": now 
    }
    return jwt.encode(token_payload, secret, algorithm="HS256")

@pytest.fixture
def client():
    with TestClient(app=app) as client:
        yield client

@pytest.fixture
def auth_headers():
    return {"Authorization": f"Bearer {get_test_token()}"}

@respx.mock
def test_sync_success_with_levelup(client: TestClient, auth_headers: dict):

    respx.post("http://127.0.0.1:8002/api/v1/sessions/batch").mock(
        return_value=Response(200, json={"total_exp_gained": 300})
    )
    
    respx.patch("http://127.0.0.1:8001/api/v1/users/me/exp/batch").mock(
        return_value=Response(200, json={"new_level": 5, "levels_gained": 2})
    )

    respx.post("http://127.0.0.1:8003/api/v1/inventory/random").mock(
        side_effect=[
            Response(201, json={"id": "item-1", "name": "Espada de Concentración"}),
            Response(201, json={"id": "item-2", "name": "Escudo de Enfoque"})
        ]
    )

    payload = SyncPayload(
        sessions=[
            SessionItem(
                activity_type="NORMAL",
                start_time="2026-05-26T10:00:00Z",
                end_time="2026-05-26T10:50:00Z",
                room_id=None
            ),
            SessionItem(
                activity_type="TIME_TRIAL",
                start_time="2026-05-26T11:00:00Z",
                end_time="2026-05-26T11:50:00Z",
                room_id="4a7b9c1d-8e2f-4a3b-9c1d-8e2f4a3b9c1d"
            )
        ]
    )

    response = client.post("/api/v1/sync", json=payload.to_dict(), headers=auth_headers)
    
    assert response.status_code == 201, f"Error interno: {response.text}"    
    data = response.json()
    
    assert data["status"] == "synchronized"
    assert data["processed_sessions_count"] == 2
    assert data["total_exp_gained"] == 300
    assert data["current_level"] == 5
    assert data["leveled_up"] is True
    assert data["levels_gained"] == 2
    assert len(data["rewards"]) == 2
    assert data["rewards"][0]["name"] == "Espada de Concentración"

@respx.mock
def test_sync_resilience_when_inventory_fails(client: TestClient, auth_headers: dict):
    
    respx.post("http://127.0.0.1:8002/api/v1/sessions/batch").mock(
        return_value=Response(200, json={"total_exp_gained": 150})
    )
    
    respx.patch("http://127.0.0.1:8001/api/v1/users/me/exp/batch").mock(
        return_value=Response(200, json={"new_level": 3, "levels_gained": 1})
    )

    respx.post("http://127.0.0.1:8003/api/v1/inventory/random").mock(
        return_value=Response(500, text="Internal Server Error")
    )

    payload = SyncPayload(
        sessions=[
            SessionItem(
                activity_type="coding",
                start_time="2026-05-26T12:00:00Z",
                end_time="2026-05-26T12:50:00Z",
                room_id=None
            )
        ]
    )

    response = client.post("/api/v1/sync", json=payload.to_dict(), headers=auth_headers)
    assert response.status_code == 201, f"Error interno: {response.text}"
    data = response.json()
    
    assert data["status"] == "synchronized"
    assert data["current_level"] == 3
    assert data["leveled_up"] is True
    assert len(data["rewards"]) == 0

def test_sync_empty_sessions(client: TestClient, auth_headers: dict):
    payload = SyncPayload(sessions=[])
    response = client.post("/api/v1/sync", json=payload.to_dict(), headers=auth_headers)
    
    assert response.status_code == 400
    assert "The request data provided is invalid." in response.json()["detail"]