import pytest
import httpx
from uuid import uuid4
from unittest.mock import patch, AsyncMock
from litestar.exceptions import PermissionDeniedException
from app.services.report_service import orchestrate_session_reports
from app.domain.structs import ReportFilters, SessionReportResponse

@pytest.mark.asyncio
async def test_student_cannot_spy_others(mock_http_client):
    logged_user = uuid4()
    other_user = uuid4()
    filters = ReportFilters(user_id=other_user)     
    
    with pytest.raises(PermissionDeniedException) as exc:
        await orchestrate_session_reports(
            mock_http_client, filters, "token", logged_user, "student"
        )
    assert "otro usuario" in exc.value.detail

@pytest.mark.asyncio
async def test_student_cannot_view_room_reports(mock_http_client):
    filters = ReportFilters(room_id=uuid4())
    
    with pytest.raises(PermissionDeniedException) as exc:
        await orchestrate_session_reports(
            mock_http_client, filters, "token", uuid4(), "student"
        )
    assert "salas enteras" in exc.value.detail

@pytest.mark.asyncio
@patch("app.services.report_service.get_room_details", new_callable=AsyncMock)
async def test_dm_cannot_view_others_rooms(mock_get_room, mock_http_client):
    dm_id = uuid4()
    filters = ReportFilters(room_id=uuid4())
    
    mock_get_room.return_value = {"creator_id": str(uuid4())} 
    
    with pytest.raises(PermissionDeniedException) as exc:
        await orchestrate_session_reports(
            mock_http_client, filters, "token", dm_id, "dm"
        )
    assert "salas que has creado" in exc.value.detail

@pytest.mark.asyncio
@patch("app.services.report_service.get_room_details", new_callable=AsyncMock)
@patch("app.services.report_service.fetch_session_reports", new_callable=AsyncMock)
async def test_dm_success_room_fetch(mock_fetch, mock_get_room, mock_http_client):
    dm_id = uuid4()
    filters = ReportFilters(room_id=uuid4())
    
    mock_get_room.return_value = {"creator_id": str(dm_id)}
    mock_fetch.return_value = SessionReportResponse(reports=[], total_count=0)
    
    result = await orchestrate_session_reports(
        mock_http_client, filters, "token", dm_id, "dm"
    )
    assert result.total_count == 0