import os
from app.clients.base import get_http_client

AUTH_URL = os.getenv("AUTH_SERVICE_URL","http://127.0.0.1:8001")

async def add_batch_exp(total_exp: int, raw_token: str) -> dict:
    async with await get_http_client() as client:
        headers = {"Authorization": f"Bearer {raw_token}"}
        payload = {"exp_to_add": total_exp}
             
        response = await client.patch(
            f"{AUTH_URL}/api/v1/users/me/exp/batch", 
            json=payload, 
            headers=headers
        )
        response.raise_for_status()
        return response.json()

async def proxy_register(payload: dict) -> dict:
    async with await get_http_client() as client:
        response = await client.post(
            f"{AUTH_URL}/api/v1/auth/register", 
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
async def proxy_login(payload: dict) -> dict:
    async with await get_http_client() as client:
        response = await client.post(
            f"{AUTH_URL}/auth/login", 
            json=payload
        )
        response.raise_for_status()
        return response.json()