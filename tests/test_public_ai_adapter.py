import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock, patch

from app.core.config import settings

# Ключ для использования в тестах
TEST_API_KEY = "test_secret_key"

@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """
    Фикстура для установки тестового API-ключа в настройки перед каждым тестом.
    """
    monkeypatch.setattr(settings, 'PUBLIC_ADAPTER_API_KEY', TEST_API_KEY)

@pytest.fixture
def mock_bank_client():
    """Мокирует клиента банка."""
    mock_client = MagicMock()
    mock_client.accounts.get_accounts = AsyncMock(return_value=[{"account_id": "v1"}])
    return mock_client

def test_tool_call_success(client: TestClient, mock_bank_client):
    """
    Тест успешного вызова инструмента через адаптер.
    """
    with patch("app.mcp.services.get_bank_client", return_value=mock_bank_client):
        request_body = {
            "user_id": "test-user",
            "tool_calls": [{
                "id": "call_123",
                "type": "function",
                "function": {
                    "name": "get_all_accounts",
                    "arguments": '{"bank_names": ["vbank"], "consent_id": "mock_consent_id"}'
                }
            }]
        }
        
        response = client.post(
            "/api/v1/public_adapter/tool_calls",
            headers={"X-API-Key": TEST_API_KEY},
            json=request_body
        )
        
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data["tool_outputs"]) == 1
        assert response_data["tool_outputs"][0]["tool_call_id"] == "call_123"
        assert '"account_id": "v1"' in response_data["tool_outputs"][0]["output"]
        
        # Проверяем, что был вызван правильный метод мок-клиента
        mock_bank_client.accounts.get_accounts.assert_called_once_with(
            "mock_access_token_for_tests", "mock_consent_id", "test-user"
        )

def test_tool_call_no_api_key(client: TestClient):
    """
    Тест ошибки при отсутствии API-ключа в заголовке.
    """
    response = client.post("/api/v1/public_adapter/tool_calls", json={})
    assert response.status_code == 403 # FastAPI вернет 403, если заголовок отсутствует
    assert "Not authenticated" in response.json()["detail"]

def test_tool_call_wrong_api_key(client: TestClient):
    """
    Тест ошибки при неверном API-ключе.
    """
    response = client.post(
        "/api/v1/public_adapter/tool_calls",
        headers={"X-API-Key": "wrong_key"},
        json={}
    )
    assert response.status_code == 403
    assert "Could not validate credentials" in response.json()["detail"]

def test_tool_call_nonexistent_tool(client: TestClient):
    """
    Тест вызова несуществующего инструмента.
    """
    request_body = {
        "user_id": "test-user",
        "tool_calls": [{
            "id": "call_456",
            "type": "function",
            "function": {
                "name": "nonexistent_tool",
                "arguments": "{}"
            }
        }]
    }
    
    response = client.post(
        "/api/v1/public_adapter/tool_calls",
        headers={"X-API-Key": TEST_API_KEY},
        json=request_body
    )
    
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data["tool_outputs"]) == 1
    assert response_data["tool_outputs"][0]["tool_call_id"] == "call_456"
    assert "Tool 'nonexistent_tool' not found" in response_data["tool_outputs"][0]["output"]
