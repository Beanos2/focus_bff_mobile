import os
import httpx
from app.clients.base import get_http_client

AUTH_URL = os.getenv("AUTH_SERVICE_URL","http://127.0.0.1:8001")

async def add_batch_exp(
    client: httpx.AsyncClient,
    total_exp: int,
    raw_token: str
) -> dict:
    headers = {"Authorization": f"Bearer {raw_token}"}
    payload = {"exp_to_add": total_exp}
            
    response = await client.patch(
        f"{AUTH_URL}/api/v1/users/me/exp/batch", 
        json=payload, 
        headers=headers
    )
    response.raise_for_status()
    return response.json()

async def proxy_register(
    client: httpx.AsyncClient,
    payload: dict
) -> dict:
        response = await client.post(
            f"{AUTH_URL}/api/v1/auth/register", 
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
async def proxy_login(
    client: httpx.AsyncClient,
    payload: dict
) -> dict:
    response = await client.post(
        f"{AUTH_URL}/api/v1/auth/login", 
        json=payload
    )
    response.raise_for_status()
    return response.json()