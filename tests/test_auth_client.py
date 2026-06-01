import pytest
from unittest.mock import AsyncMock, MagicMock
from app.clients.auth_client import proxy_register, proxy_login

@pytest.mark.asyncio
async def test_proxy_register_success():
    mock_client = AsyncMock()
    mock_response = MagicMock()
    
    mock_response.json.return_value = {"id": "123", "email": "test@mail.com"}
    mock_client.post.return_value = mock_response

    payload = {"email": "test@mail.com", "password": "123", "role": "student"}
    
    result = await proxy_register(client=mock_client, payload=payload)

    assert result["email"] == "test@mail.com"
    mock_client.post.assert_called_once()

@pytest.mark.asyncio
async def test_proxy_login_success():
    mock_client = AsyncMock()
    mock_response = MagicMock()
    
    mock_response.json.return_value = {"access_token": "token_falso", "token_type": "bearer"}
    mock_client.post.return_value = mock_response

    payload = {"email": "test@mail.com", "password": "123"}
    
    result = await proxy_login(client=mock_client, payload=payload)

    assert "access_token" in result
    assert result["access_token"] == "token_falso"
    mock_client.post.assert_called_once()