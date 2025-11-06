from fastapi import APIRouter, Depends, HTTPException
from app.llm_integration.schemas import AgentQueryRequest, AgentResponse
from app.llm_integration.services import LLMAgentService

router = APIRouter()

# Инициализируем LLMAgentService один раз при запуске приложения
llm_agent_service = LLMAgentService()

@router.post("/chat", response_model=AgentResponse)
async def chat_with_agent(request: AgentQueryRequest) -> AgentResponse:
    """
    Отправляет запрос пользователя ИИ-агенту и получает ответ.
    """
    try:
        response = await llm_agent_service.process_user_query(request.user_id, request.query)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обработке запроса ИИ-агентом: {e}")
