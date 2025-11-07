from fastapi import Depends
from app.mcp.dependencies import get_mcp_service
from app.mcp.services import MCPService
from app.public_ai_adapter.services import PublicAIAdapterService

def get_public_ai_adapter_service(
    mcp_service: MCPService = Depends(get_mcp_service)
) -> PublicAIAdapterService:
    """
    Зависимость FastAPI для получения экземпляра PublicAIAdapterService.
    """
    return PublicAIAdapterService(mcp_service=mcp_service)
