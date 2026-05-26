import os
import uvicorn
from litestar import Litestar, get
from dotenv import load_dotenv

load_dotenv()

from app.core.security import jwt_auth
from app.api.v1.sync_controller import SyncController


PUERTO = int(os.getenv("LITESTAR_PORT", 8000))

@get("/health")
async def health_check() -> dict:
    return {"status": "ok", "service": "bff_orchestrator"}

app = Litestar(
    route_handlers=[health_check, SyncController],
    on_app_init=[jwt_auth.on_app_init],
)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=PUERTO, reload=True)