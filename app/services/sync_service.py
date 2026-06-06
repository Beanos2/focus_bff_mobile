import httpx
from litestar.exceptions import HTTPException
from litestar import status_codes
from app.clients import stats_client, auth_client, inv_client
from app.domain.structs import SyncPayload, SyncResponse

async def orchestrate_sync(
    http_client: httpx.AsyncClient,
    data: SyncPayload, raw_token: str
) -> SyncResponse:
    
    if not data.sessions:
        raise HTTPException(
            detail="The request data provided is invalid or empty.",
            status_code=status_codes.HTTP_400_BAD_REQUEST
        )

    try:
        stats_data = await stats_client.process_batch_sessions(client=http_client, payload=data, raw_token=raw_token)
        auth_data = await auth_client.add_batch_exp(
            client=http_client, 
            total_exp=stats_data.total_exp_gained, 
            raw_token=raw_token
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            detail="Error procesando la sincronización en los servicios internos.", 
            status_code=e.response.status_code
        )
    except httpx.RequestError:
        raise HTTPException(
            detail="Servicios internos fuera de línea.", 
            status_code=status_codes.HTTP_503_SERVICE_UNAVAILABLE
        )

    rewards_otorgadas = []
    if auth_data.levels_gained > 0:
        for _ in range(auth_data.levels_gained):
            try:
                reward = await inv_client.grant_random_item(client=http_client, raw_token=raw_token)
                rewards_otorgadas.append(reward)
            except Exception:
                pass 

    return SyncResponse(
        status="synchronized",
        processed_sessions_count=len(data.sessions),
        total_exp_gained=stats_data.total_exp_gained,
        current_level=auth_data.new_level,
        leveled_up=auth_data.leveled_up,
        levels_gained=auth_data.levels_gained,
        rewards=rewards_otorgadas    
    )