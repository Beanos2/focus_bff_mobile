import os
from app.clients.base import get_http_client
import httpx

STATS_URL = os.getenv("STATS_SERVICE_URL","http://127.0.0.1:8002")

async def process_batch_sessions(
    client: httpx.AsyncClient,
    sessions: list[dict], 
    raw_token: str
) -> dict:
    headers = {"Authorization": f"Bearer {raw_token}"}
    payload = {"sessions": sessions}
    
    response = await client.post(
        f"{STATS_URL}/api/v1/sessions/batch", 
        json=payload, 
        headers=headers
    )
    response.raise_for_status()
    return response.json()

async def fetch_session_reports(
    client: httpx.AsyncClient, 
    query_params: dict, 
    raw_token: str
) -> dict:
    headers = {"Authorization": f"Bearer {raw_token}"}
    
    response = await client.get(
        f"{STATS_URL}/api/v1/sessions/reports",
        params=query_params,
        headers=headers
    )
    response.raise_for_status()
    return response.json()