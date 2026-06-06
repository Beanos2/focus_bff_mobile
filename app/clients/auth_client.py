import httpx
import os
import msgspec
from app.domain.structs import (
    RegisterPayload, RegisterResponse, LoginPayload, TokenResponse,
    BatchExpPayload, BatchExpResponse
)

AUTH_URL = os.getenv("AUTH_SERVICE_URL","http://127.0.0.1:8001")

async def proxy_register(
    client: httpx.AsyncClient,
    payload: RegisterPayload
) -> RegisterResponse:
    url = f"{AUTH_URL}/api/v1/auth/register"
    content = msgspec.json.encode(payload)
    response = await client.post(url, content=content, headers={"Content-Type": "application/json"})
    response.raise_for_status()
    return msgspec.json.decode(response.content, type=RegisterResponse)

async def proxy_login(
    client: httpx.AsyncClient,
    payload: LoginPayload
) -> TokenResponse:
    url = f"{AUTH_URL}/api/v1/auth/login"
    content = msgspec.json.encode(payload)
    response = await client.post(url, content=content, headers={"Content-Type": "application/json"})
    response.raise_for_status()
    return msgspec.json.decode(response.content, type=TokenResponse)

async def add_batch_exp(
    client: httpx.AsyncClient,
    total_exp: int, raw_token: str
) -> BatchExpResponse:

    url = f"{AUTH_URL}/api/v1/users/me/exp/batch"
    headers = {"Authorization": f"Bearer {raw_token}", "Content-Type": "application/json"}
    content = msgspec.json.encode(BatchExpPayload(exp_to_add=total_exp))
    response = await client.patch(url, content=content, headers=headers)
    response.raise_for_status()
    return msgspec.json.decode(response.content, type=BatchExpResponse)