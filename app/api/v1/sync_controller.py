from litestar import Controller, post,status_codes, Request,status_codes
import httpx
from litestar.datastructures import State
from litestar.exceptions import HTTPException
from app.clients import stats_client, auth_client, inv_client
from app.domain.structs import SyncPayload, SyncResponse, RewardItem

class SyncController(Controller):
    path = "/sync"
    tags = ["Sincronización"]
    
    @post()
    async def sync_offline_data(self, request: Request, state: State, data: SyncPayload) -> SyncResponse:
        
        http_client = state.http_client

        auth_header = request.headers.get("Authorization")
        raw_token = auth_header.replace("Bearer ", "") if auth_header else ""


        if not data.sessions:
            raise HTTPException(
                detail="The request data provided is invalid.",
                status_code=status_codes.HTTP_400_BAD_REQUEST
            )

        sessions_dict = data.to_dict().get("sessions", [])

        try:
            stats_data = await stats_client.process_batch_sessions(
                client=http_client, 
                sessions=sessions_dict, 
                raw_token=raw_token
            )
            total_exp = stats_data.get("total_exp_gained", 0)

            auth_data = await auth_client.add_batch_exp(
                client=http_client, 
                total_exp=total_exp, 
                raw_token=raw_token
            )
            new_level = auth_data.get("new_level", -1)
            levels_gained = auth_data.get("levels_gained", 0)
            
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
        if levels_gained > 0:
            for _ in range(levels_gained):
                try:
                    reward_dict = await inv_client.grant_random_item(
                        client=http_client, 
                        raw_token=raw_token
                    )
                    if reward_dict:
                        rewards_otorgadas.append(RewardItem.from_dict(reward_dict))
                except Exception:
                    pass

        response = SyncResponse(
            status="synchronized",
            processed_sessions_count=len(data.sessions),
            total_exp_gained=total_exp,
            current_level=new_level ,
            leveled_up=levels_gained > 0,
            levels_gained=levels_gained,
            rewards=rewards_otorgadas    
        )
        return response