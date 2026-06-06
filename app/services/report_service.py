import httpx
from uuid import UUID
from litestar.exceptions import HTTPException, PermissionDeniedException

from app.clients.stats_client import fetch_session_reports
from app.clients.room_client import get_room_details
from app.domain.structs import SessionReportResponse, ReportFilters


async def orchestrate_session_reports(
    http_client: httpx.AsyncClient,
    filters: ReportFilters,
    raw_token: str,
    logged_user_id: UUID,
    user_role: str
) -> SessionReportResponse:
    
    if filters.user_id and filters.user_id != logged_user_id and user_role == "student":
        raise PermissionDeniedException("No tienes permiso para ver los informes de otro usuario.")
    
    if filters.room_id:
        if user_role == "student":
            raise PermissionDeniedException("Los estudiantes no pueden solicitar informes de salas enteras.")
        elif user_role == "dm":
            try:
                room_info = await get_room_details(
                    client=http_client, room_id=filters.room_id, 
                    raw_token=raw_token, logged_user_id=logged_user_id
                )
                if room_info.get("creator_id") != str(logged_user_id):
                    raise PermissionDeniedException("Solo puedes ver estadísticas de las salas que has creado.")
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise HTTPException(detail="La sala solicitada no existe.", status_code=404)
                raise HTTPException(detail="Error al consultar la sala.", status_code=500)
            except httpx.RequestError:
                raise HTTPException(detail="Servicio de salas fuera de línea.", status_code=503)
    
    try:
        return await fetch_session_reports(client=http_client, filters=filters, raw_token=raw_token)
    except httpx.HTTPStatusError as e:
        raise HTTPException(detail="Error en ms_stats.", status_code=e.response.status_code)
    except httpx.RequestError:
        raise HTTPException(detail="Estadísticas fuera de línea.", status_code=503)