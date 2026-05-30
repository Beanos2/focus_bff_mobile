import pytest
import httpx
from litestar import Litestar
from litestar.testing import TestClient
from unittest.mock import patch, AsyncMock

from app.api.v1.auth_controller import AuthBFFController

@pytest.fixture
def client():
    test_app = Litestar(route_handlers=[AuthBFFController])
    with TestClient(app=test_app) as client:
        yield client

@patch("app.api.v1.auth_controller.proxy_register", new_callable=AsyncMock) 
def test_controller_register_success(mock_proxy, client: TestClient)-> None:
    mock_proxy.return_value = {"id": "123", "email": "test@mail.com"}
    
    response = client.post("/api/v1/auth/register", json={"email": "test", "password": "123"})
    
    assert response.status_code == 201
    assert response.json()["email"] == "test@mail.com"

@patch("app.api.v1.auth_controller.proxy_login", new_callable=AsyncMock)
def test_controller_login_success(mock_proxy, client: TestClient) -> None:
    mock_proxy.return_value = {"access_token": "token", "token_type": "bearer"}
    
    response = client.post("/api/v1/auth/login", json={"email": "test", "password": "123"})
    
    assert response.status_code == 201
    assert "access_token" in response.json()

@patch("app.api.v1.auth_controller.proxy_login", new_callable=AsyncMock)
def test_controller_login_handles_http_error(mock_proxy, client: TestClient) -> None:

    dummy_request = httpx.Request("POST", "http://fake-auth/login")
    dummy_response = httpx.Response(401, request=dummy_request, json={"detail": "Bad creds"})
    
    mock_proxy.side_effect = httpx.HTTPStatusError(
        message="Unauthorized",
        request=dummy_request,
        response=dummy_response
    )
    
    response = client.post("/api/v1/auth/login", json={"email": "test", "password": "mal"})
    
    assert response.status_code == 401
    assert "Credenciales inválidas" in response.json()["detail"]