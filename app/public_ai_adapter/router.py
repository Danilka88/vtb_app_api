from fastapi import APIRouter, Depends, Security
from app.public_ai_adapter.schemas import ToolCallRequest, ToolCallResponse
from app.public_ai_adapter.services import PublicAIAdapterService
from app.public_ai_adapter.dependencies import get_public_ai_adapter_service
from app.public_ai_adapter.security import get_api_key

router = APIRouter()

@router.post(
    "/tool_calls",
    response_model=ToolCallResponse,
    dependencies=[Security(get_api_key)]
)
async def handle_tool_calls(
    request: ToolCallRequest,
    adapter_service: PublicAIAdapterService = Depends(get_public_ai_adapter_service)
) -> ToolCallResponse:
    """
    Принимает и обрабатывает запросы на вызов инструментов от внешних ИИ-моделей.
    Эндпоинт защищен API-ключом (заголовок X-API-Key).
    """
    tool_outputs = await adapter_service.execute_tool_calls(
        user_id=request.user_id,
        tool_calls=request.tool_calls
    )
    return ToolCallResponse(tool_outputs=tool_outputs)
