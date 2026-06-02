from litestar import Controller, get

class MsStatusController(Controller):
    tags = ["Estatus"]
    
    @get("/health", opt={"publico": True})
    async def health_check(self) -> dict:
        return {"status": "ok", "service": "bff_orchestrator"}
