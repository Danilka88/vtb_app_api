import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from main import app
from app.db.database import get_db
from app.llm_integration.services import LLMAgentService
from app.llm_integration.schemas import AgentQueryRequest, AgentResponse

# --- Fixtures ---

@pytest.fixture
def mock_db_session():
    """
    Фикстура для мокирования сессии базы данных.
    """
    return MagicMock(spec=Session)

@pytest.fixture(name="test_client")
def test_client_fixture(mock_db_session):
    """
    Фикстура для тестового клиента FastAPI с переопределенной зависимостью get_db.
    """
    def override_get_db():
        yield mock_db_session
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

@pytest.fixture
def mock_llm_agent_service():
    """
    Мокируем LLMAgentService для изоляции тестов.
    """
    service = AsyncMock(spec=LLMAgentService)
    service.process_user_query.return_value = AgentResponse(
        response="Mocked AI response",
        raw_response={"output": "Mocked AI response"}
    )
    return service

# --- Tests ---

@pytest.mark.asyncio
async def test_chat_with_agent_success(test_client: TestClient, mock_llm_agent_service: AsyncMock): # Используем мок сервиса
    """
    Тест успешного взаимодействия с ИИ-агентом через API.
    """
    user_id = "test-user-1"
    query = "Покажи мои счета"

    # Патчим глобальный экземпляр LLMAgentService в роутере
    with patch("app.llm_integration.router.llm_agent_service", new=mock_llm_agent_service):
        response = test_client.post(
            "/api/v1/llm/chat",
            json={
                "user_id": user_id,
                "query": query
            }
        )

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["response"] == "Mocked AI response"
        mock_llm_agent_service.process_user_query.assert_called_once_with(user_id, query)

@pytest.mark.asyncio
async def test_chat_with_agent_error(test_client: TestClient, mock_llm_agent_service: AsyncMock):
    """
    Тест обработки ошибок при взаимодействии с ИИ-агентом.
    """
    user_id = "test-user-1"
    query = "Что-то пошло не так"

    mock_llm_agent_service.process_user_query.side_effect = Exception("Internal AI error")

    with patch("app.llm_integration.router.llm_agent_service", new=mock_llm_agent_service):
        response = test_client.post(
            "/api/v1/llm/chat",
            json={
                "user_id": user_id,
                "query": query
            }
        )

        assert response.status_code == 500
        response_data = response.json()
        assert "Ошибка при обработке запроса ИИ-агентом" in response_data["detail"]
        mock_llm_agent_service.process_user_query.assert_called_once_with(user_id, query)
