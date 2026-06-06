import pytest
import httpx
import msgspec
from unittest.mock import patch
from app.clients.auth_client import proxy_login, add_batch_exp
from app.domain.structs import LoginPayload, TokenResponse, BatchExpResponse

@pytest.mark.asyncio
@patch.object(httpx.AsyncClient, "post")
async def test_proxy_login_client(mock_post, mock_http_client):
    mock_res = TokenResponse(access_token="jwt_secret_token", token_type="bearer")
    mock_post.return_value = httpx.Response(
    200, 
    content=msgspec.json.encode(mock_res),
    request=httpx.Request("POST", "http://test.com") 
)     
    payload = LoginPayload(email="test@dev.com", password="password123")
    res = await proxy_login(mock_http_client, payload)
    
    assert res.access_token == "jwt_secret_token"
    mock_post.assert_called_once()  

@pytest.mark.asyncio
@patch.object(httpx.AsyncClient, "patch")
async def test_add_batch_exp_client(mock_patch, mock_http_client):
    mock_res = BatchExpResponse(new_level=12, levels_gained=2, leveled_up=True)
    mock_patch.return_value = httpx.Response(
    200, 
    content=msgspec.json.encode(mock_res),
    request=httpx.Request("POST", "http://test.com") 
)
    res = await add_batch_exp(mock_http_client, total_exp=450, raw_token="token_string")
    
    assert res.new_level == 12
    assert res.leveled_up is True
    mock_patch.assert_called_once()