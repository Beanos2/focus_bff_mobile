import os
import pytest
import respx
import httpx
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from litestar.testing import TestClient

os.environ["SECRET_KEY"] = "clave_super_secreta"
os.environ["STATS_SERVICE_URL"] = "http://127.0.0.1:8002"
os.environ["ROOMS_SERVICE_URL"] = "http://127.0.0.1:8004" 
from app.main import app 


def get_auth_headers(role: str, user_id: str) -> dict:
    import jwt
    from app.core.security import jwt_auth 
    
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id, 
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=15)
    }
    token = jwt.encode(payload, jwt_auth.token_secret, algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
@respx.mock
async def test_student_cannot_query_other_users_data():
    student_id = str(uuid4())
    other_user_id = str(uuid4())
    headers = get_auth_headers(role="student", user_id=student_id)

    with TestClient(app=app) as client:
        response = client.get(
            f"/api/v1/sessions/reports?user_id={other_user_id}", 
            headers=headers
        )

    assert response.status_code == 403


@pytest.mark.asyncio
@respx.mock
async def test_dm_can_query_owned_room():
    dm_id = str(uuid4())
    room_id = str(uuid4())
    headers = get_auth_headers(role="dm", user_id=dm_id)

    respx.get(url__startswith=f"http://127.0.0.1:8004/api/v1/rooms/{room_id}").mock(
        return_value=httpx.Response(200, json={"id": room_id, "creator_id": dm_id})
    )
    
    respx.get(url__startswith="http://127.0.0.1:8002/api/v1/sessions/reports").mock(
        return_value=httpx.Response(200, json={
            "reports": [], "total_count": 0
        })
    )

    with TestClient(app=app) as client:
        response = client.get(
            f"/api/v1/sessions/reports?room_id={room_id}", 
            headers=headers
        )

    assert response.status_code == 200


@pytest.mark.asyncio
@respx.mock
async def test_dm_cannot_query_unowned_room():
    dm_id = str(uuid4())
    other_dm_id = str(uuid4())
    room_id = str(uuid4())
    headers = get_auth_headers(role="dm", user_id=dm_id)

    respx.get(url__startswith=f"http://127.0.0.1:8004/api/v1/rooms/{room_id}").mock(
        return_value=httpx.Response(200, json={"id": room_id, "creator_id": other_dm_id})
    )

    with TestClient(app=app) as client:
        response = client.get(
            f"/api/v1/sessions/reports?room_id={room_id}", 
            headers=headers
        )

    assert response.status_code == 403