from uuid import UUID
from typing import Annotated
from litestar import Controller, get, Request
from litestar.datastructures import State
from litestar.params import Parameter

from app.domain.structs import SessionReportResponse, ReportFilters
from app.services.report_service import orchestrate_session_reports

class SessionsReportsController(Controller):
    path = "/sessions"
    tags = ["Reportes"]

    @get("/reports")
    async def get_reports(
        self, 
        request: Request,
        state: State,
        filters: Annotated[ReportFilters, Parameter(query="*")]
    ) -> SessionReportResponse:
        
        auth_header = request.headers.get("Authorization")
        raw_token = auth_header.replace("Bearer ", "") if auth_header else ""
        
        user_data = request.user
        logged_user_id = UUID(str(user_data.get("sub")))
        user_role = user_data.get("role", "student")

        return await orchestrate_session_reports(
            http_client=state.http_client,
            filters=filters,
            raw_token=raw_token,
            logged_user_id=logged_user_id,
            user_role=user_role
        )