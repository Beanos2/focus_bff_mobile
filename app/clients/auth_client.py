import os
from app.clients.base import get_http_client

AUTH_URL = os.getenv("AUTH_SERVICE_URL")

async def add_batch_exp(total_exp: int, raw_token: str) -> dict:
    async with await get_http_client() as client:
        headers = {"Authorization": f"Bearer {raw_token}"}
        payload = {"exp_to_add": total_exp}
        
        #TODO: change to real direction        
        response = await client.patch(
            f"{AUTH_URL}/api/v1/users/me/exp", 
            json=payload, 
            headers=headers
        )
        response.raise_for_status()
        return response.json()