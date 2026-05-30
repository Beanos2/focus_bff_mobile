from litestar import Controller, get

class MsStatusController(Controller):
    
    @get("/health")
    async def health_check(self) -> dict:
        return {"status": "ok", "service": "bff_orchestrator"}
