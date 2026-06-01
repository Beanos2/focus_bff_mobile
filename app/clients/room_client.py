import httpx

async def get_room_details(
    client: httpx.AsyncClient, 
    room_id: str, 
    raw_token: str,
    logged_user_id: str
) -> dict:
    #TODO: when the room ms is ready remplace this stuff with the client call
    return {
        "id": room_id,
        "creator_id": logged_user_id, 
        "name": "Sala Simulada"
    }