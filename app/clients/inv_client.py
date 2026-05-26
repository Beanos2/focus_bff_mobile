import os
from app.clients.base import get_http_client

INV_URL = os.getenv("INVENTORY_SERVICE_URL")

async def grant_random_item(raw_token: str) -> dict:
    async with await get_http_client() as client:
        headers = {"Authorization": f"Bearer {raw_token}"}

        #TODO: change to real direction
        response = await client.post(
            f"{INV_URL}/api/v1/inventory/random", 
            headers=headers
        )
        response.raise_for_status()
        return response.json()