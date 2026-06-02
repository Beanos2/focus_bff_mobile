import httpx
from litestar import Controller, post,status_codes
from litestar.datastructures import State
from litestar.exceptions import HTTPException
from app.domain.structs import RegisterPayload, RegisterResponse, LoginPayload, TokenResponse

from app.clients.auth_client import proxy_register, proxy_login

class AuthController(Controller):
    path = "/auth"
    tags = ["Autenticación"]

    @post("/register", opt={"publico": True})
    async def register(self, state: State, data: RegisterPayload) -> RegisterResponse:
        http_client = state.http_client
        try:
            response_dict = await proxy_register(http_client,data.to_dict())
            return RegisterResponse.from_dict(response_dict)          
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                detail="Error en el registro (¿correo duplicado?)", 
                status_code=e.response.status_code
            )
        except httpx.RequestError:
            raise HTTPException(
                detail="El servicio de autenticación se encuentra fuera de línea.", 
                status_code=status_codes.HTTP_503_SERVICE_UNAVAILABLE
            )
        
    @post("/login", opt={"publico": True})
    async def login(self, state: State, data: LoginPayload) -> TokenResponse:
        http_client = state.http_client
        try:
            response_dict = await proxy_login(client=http_client, payload=data.to_dict())
            return TokenResponse.from_dict(response_dict)
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                detail="Credenciales inválidas", 
                status_code=e.response.status_code
            )
        except httpx.RequestError:
            raise HTTPException(
                detail="El servicio de autenticación se encuentra fuera de línea.", 
                status_code=status_codes.HTTP_503_SERVICE_UNAVAILABLE
            )