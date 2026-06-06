from litestar import Controller, post, Request
from litestar.datastructures import State
from app.domain.structs import SyncPayload, SyncResponse
from app.services.sync_service import orchestrate_sync

class SyncController(Controller):
    path = "/sync"
    tags = ["Sincronización"]
    
    @post()
    async def sync_offline_data(self, request: Request, state: State, data: SyncPayload) -> SyncResponse:
        auth_header = request.headers.get("Authorization")
        raw_token = auth_header.replace("Bearer ", "") if auth_header else ""

        return await orchestrate_sync(
            http_client=state.http_client,
            data=data,
            raw_token=raw_token
        )