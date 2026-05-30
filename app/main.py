import os
import uvicorn
from litestar import Litestar
from dotenv import load_dotenv
from app.core.security import jwt_auth
from app.api.v1.sync_controller import SyncController
from app.api.v1.auth_controller import AuthController
from app.api.v1.ms_status_controller import MsStatusController

load_dotenv()


PUERTO = int(os.getenv("LITESTAR_PORT", 8000))


app = Litestar(
    path="api/v1",
    route_handlers=[
        MsStatusController,
        SyncController,
        AuthController
    ],
    on_app_init=[jwt_auth.on_app_init],
)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=PUERTO, reload=True)