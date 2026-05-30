import httpx
from litestar import Controller, post
from litestar.exceptions import HTTPException
from app.domain.structs import RegisterPayload, RegisterResponse, LoginPayload, TokenResponse

from app.clients.auth_client import proxy_register, proxy_login

class AuthController(Controller):
    path = "/auth"
    tags = ["Autenticación"]

    @post("/register")
    async def register(self, data: RegisterPayload) -> RegisterResponse:
        try:
            response_dict = await proxy_register(data.to_dict())
            return RegisterResponse.from_dict(response_dict)          
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                detail="Error en el registro (¿Correo duplicado?)", 
                status_code=e.response.status_code
            )
        
    @post("/login")
    async def login(self, data: LoginPayload) -> TokenResponse:
        try:
            response_dict = await proxy_login(data.to_dict())
            return TokenResponse.from_dict(response_dict)
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                detail="Credenciales inválidas", 
                status_code=e.response.status_code
            )