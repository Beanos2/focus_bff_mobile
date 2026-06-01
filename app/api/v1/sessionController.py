import httpx
from typing import Optional, Annotated
from litestar import Controller, get, status_codes, Request
from litestar.exceptions import HTTPException, PermissionDeniedException
from litestar.datastructures import State
from litestar.params import Parameter

from app.clients.stats_client import fetch_session_reports
from app.clients.room_client import get_room_details
from app.domain.structs import SessionReportResponse

class SessionsBFFController(Controller):
    path = "/api/v1/sessions"
    tags = ["Sesiones e Informes"]

    @get("/reports")
    async def get_reports(
        self, 
        request: Request,
        state: State,
        user_id: Annotated[Optional[str], Parameter(required=False)] = None,
        room_id: Annotated[Optional[str], Parameter(required=False)] = None,
        start_date: Annotated[Optional[str], Parameter(required=False)] = None,
        end_date: Annotated[Optional[str], Parameter(required=False)] = None,
        sort_order: Annotated[str, Parameter(required=False)] = "desc",
        limit: Annotated[int, Parameter(required=False)] = 50,
        offset: Annotated[int, Parameter(required=False)] = 0
    ) -> SessionReportResponse:
        
        http_client = state.http_client
        auth_header = request.headers.get("Authorization")
        raw_token = auth_header.replace("Bearer ", "") if auth_header else ""
        
        logged_user_id = str(request.user)
        user_role = "student"
        
        if hasattr(request.auth, "extras"):
            user_role = request.auth.extras.get("role", "student")
        elif isinstance(request.auth, dict):
            user_role = request.auth.get("role", "student")

        if room_id:
            if user_role == "student":
                raise PermissionDeniedException("Los estudiantes no pueden solicitar informes de salas enteras.")
            elif user_role == "dm":
                try:
                    room_info = await get_room_details(
                        client=http_client, room_id=room_id, raw_token=raw_token, logged_user_id=logged_user_id
                    )
                    if room_info.get("creator_id") != logged_user_id:
                        raise PermissionDeniedException("Solo puedes ver estadísticas de las salas que has creado.")
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 404:
                        raise HTTPException(detail="La sala solicitada no existe.", status_code=404)
                    raise HTTPException(detail="Error al consultar la sala.", status_code=500)
                except httpx.RequestError:
                    raise HTTPException(detail="Servicio de salas fuera de línea.", status_code=503)

        if user_id and user_id != logged_user_id and user_role == "student":
            raise PermissionDeniedException("No tienes permiso para ver los informes de otro usuario.")

        filters = {
            "user_id": user_id, "room_id": room_id, "start_date": start_date,
            "end_date": end_date, "sort_order": sort_order, "limit": limit, "offset": offset
        }
        clean_filters = {k: v for k, v in filters.items() if v is not None}

        try:
            response_dict = await fetch_session_reports(client=http_client, query_params=clean_filters, raw_token=raw_token)
            return SessionReportResponse.from_dict(response_dict)
        except httpx.HTTPStatusError as e:
            raise HTTPException(detail="Error en ms_stats.", status_code=e.response.status_code)
        except httpx.RequestError:
            raise HTTPException(detail="Estadísticas fuera de línea.", status_code=503)