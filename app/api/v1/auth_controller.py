import httpx
from litestar import Controller, post
from litestar.exceptions import HTTPException


from app.clients.auth_client import proxy_register, proxy_login

class AuthController(Controller):
    path = "/auth"

    @post("/register")
    async def register(self, data: dict) -> dict:
        try:
            return await proxy_register(data)
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                detail="Error en el registro (¿Correo duplicado?)", 
                status_code=e.response.status_code
            )
        
    @post("/login")
    async def login(self, data: dict) -> dict:
        try:
            return await proxy_login(data)
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                detail="Credenciales inválidas", 
                status_code=e.response.status_code
            )