import os
import httpx

ROOMS_URL = os.getenv("ROOMS_SERVICE_URL", "http://127.0.0.1:8004")

async def get_room_details(
    client: httpx.AsyncClient, 
    room_id: str, 
    raw_token: str,
    logged_user_id: str 
) -> dict:
    
    headers = {"Authorization": f"Bearer {raw_token}"}
    
    response = await client.get(
        f"{ROOMS_URL}/api/v1/rooms/{room_id}", 
        headers=headers
    )
    response.raise_for_status()
    return response.json()