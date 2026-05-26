import os
from app.clients.base import get_http_client

STATS_URL = os.getenv("STATS_SERVICE_URL")

async def process_batch_sessions(sessions: list[dict], raw_token: str) -> dict:
    async with await get_http_client() as client:
        headers = {"Authorization": f"Bearer {raw_token}"}
        payload = {"sessions": sessions}
        
        #TODO: change to real direction
        response = await client.post(
            f"{STATS_URL}/api/v1/sessions/batch", 
            json=payload, 
            headers=headers
        )
        response.raise_for_status()
        return response.json()