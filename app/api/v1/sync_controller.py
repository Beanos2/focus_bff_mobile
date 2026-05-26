from litestar import Controller, post,status_codes, Request
from litestar.exceptions import HTTPException
from app.clients import stats_client, auth_client, inv_client

class SyncController(Controller):
    path = "/api/v1/sync"

    @post()
    async def sync_offline_data(self, request: Request, data: dict) -> dict:
        
        auth_header = request.headers.get("Authorization")
        raw_token = auth_header.replace("Bearer ", "") if auth_header else ""

        sessions = data.get("sessions", [])

        if not sessions:
            raise HTTPException(
                detail="The request data provided is invalid.",
                status_code=status_codes.HTTP_400_BAD_REQUEST
            )
    
        stats_data = await stats_client.process_batch_sessions(sessions, raw_token)
        total_exp = stats_data.get("total_exp_gained", 0)

    
        auth_data = await auth_client.add_batch_exp(total_exp, raw_token)
        new_level = auth_data.get("new_level")
        levels_gained = auth_data.get("levels_gained", 0)


        rewards_otorgadas = []
        if levels_gained > 0:
            for _ in range(levels_gained):
                try:
                    reward = await inv_client.grant_random_item(raw_token)
                    if reward:
                        rewards_otorgadas.append(reward)
                except Exception:
                    pass

        return {
            "status": "synchronized",
            "processed_sessions_count": len(sessions),
            "total_exp_gained": total_exp,
            "current_level": new_level,
            "leveled_up": levels_gained > 0,
            "levels_gained": levels_gained,
            "rewards": rewards_otorgadas
        }