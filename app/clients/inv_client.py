import os
import httpx
from app.clients.base import get_http_client

INV_URL = os.getenv("INVENTORY_SERVICE_URL","http://127.0.0.1:8003")

async def grant_random_item(
    client: httpx.AsyncClient,
    raw_token: str
) -> dict:
    headers = {"Authorization": f"Bearer {raw_token}"}

    #TODO: change to real direction
    response = await client.post(
        f"{INV_URL}/api/v1/inventory/random", 
        headers=headers
    )
    response.raise_for_status()
    return response.json()