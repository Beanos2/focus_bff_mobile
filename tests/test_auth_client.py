import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import httpx

from app.clients.auth_client import proxy_register, proxy_login

@pytest.fixture
def mock_http_client():
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    
    mock_client_instance = AsyncMock()
    mock_client_instance.post.return_value = mock_response
    
    mock_cm = AsyncMock()
    mock_cm.__aenter__.return_value = mock_client_instance
    
    return mock_cm, mock_client_instance, mock_response

@pytest.mark.asyncio
@patch("app.clients.auth_client.get_http_client")
async def test_proxy_register_success(mock_get_client, mock_http_client):
    mock_cm, mock_client_instance, mock_response = mock_http_client
    mock_get_client.return_value = mock_cm
    
    mock_response.json.return_value = {"id": "123", "email": "test@mail.com"}
    
    payload = {"email": "test@mail.com", "password": "123", "role": "student"}
    result = await proxy_register(payload)
    
    assert result["email"] == "test@mail.com"
    mock_client_instance.post.assert_called_once()
    mock_response.raise_for_status.assert_called_once()

@pytest.mark.asyncio
@patch("app.clients.auth_client.get_http_client")
async def test_proxy_login_success(mock_get_client, mock_http_client):
    mock_cm, mock_client_instance, mock_response = mock_http_client
    mock_get_client.return_value = mock_cm
    
    mock_response.json.return_value = {"access_token": "token_falso", "token_type": "bearer"}
    
    payload = {"email": "test@mail.com", "password": "123"}
    result = await proxy_login(payload)
    
    assert result["access_token"] == "token_falso"
    mock_client_instance.post.assert_called_once()