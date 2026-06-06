import httpx
from litestar.exceptions import HTTPException
from litestar import status_codes
from app.domain.structs import RegisterPayload, RegisterResponse, LoginPayload, TokenResponse
from app.clients.auth_client import proxy_register, proxy_login

async def orchestrate_register(
    http_client: httpx.AsyncClient,
    data: RegisterPayload
) -> RegisterResponse:
    try:
        return await proxy_register(client=http_client, payload=data)
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
    
async def orchestrate_login(
    http_client: httpx.AsyncClient,
    data: LoginPayload
) -> TokenResponse:
    try:
        return await proxy_login(client=http_client, payload=data)
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