import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from main import app
from app.db.database import get_db
from app.mcp.services import MCPService
from app.mcp.schemas import MultiBankAccountsRequest, MultiBankConsentRequest, BankOperationResponse
from app.utils.bank_clients import get_bank_client
from app.banks.base_client import BaseBankClient
from app.banks.services.accounts.base import BaseAccountsService
from app.banks.services.payments.base import BasePaymentsService
from app.banks.services.products.base import BaseProductsService
from app.core.config import settings
from app.auth_manager.services import BaseAuthManager, OAuth2AuthManager
from app.auth_manager.dependencies import get_auth_manager
from app.auth_manager.exceptions import TokenFetchError
from httpx import HTTPStatusError, Response

# --- Fixtures --- 

@pytest.fixture
def mock_db_session():
    """Фикстура для мокирования сессии базы данных."""
    return MagicMock(spec=Session)

@pytest.fixture
def mock_auth_manager():
    """Фикстура для мокирования AuthManager."""
    mock = MagicMock(spec=BaseAuthManager)
    mock.get_access_token = AsyncMock(return_value="mock_access_token")
    return mock

@pytest.fixture
def mock_bank_client():
    """Фикстура для мокирования BaseBankClient и его сервисов."""
    mock_client = MagicMock(spec=BaseBankClient)
    mock_client._async_client = AsyncMock()
    mock_client.api_url = "http://mockbank.com"
    mock_client.accounts = MagicMock(spec=BaseAccountsService)
    mock_client.payments = MagicMock(spec=BasePaymentsService)
    mock_client.products = MagicMock(spec=BaseProductsService)
    mock_client.create_consent = AsyncMock()
    mock_client.create_payment_consent = AsyncMock()
    mock_client.create_product_agreement_consent = AsyncMock()
    return mock_client

@pytest.fixture
def mcp_service(mock_db_session, mock_auth_manager):
    """Фикстура для MCPService с мокированными зависимостями."""
    return MCPService(db=mock_db_session, auth_manager=mock_auth_manager)

@pytest.fixture(name="test_client")
def test_client_fixture(mock_db_session, mock_auth_manager):
    """Фикстура для тестового клиента FastAPI с переопределенными зависимостями."""
    def override_get_db():
        yield mock_db_session
    
    def override_get_auth_manager():
        return mock_auth_manager

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_auth_manager] = override_get_auth_manager
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

# --- Tests for MCPService --- 

@pytest.mark.asyncio
async def test_get_all_accounts_consent_error(mcp_service, mock_auth_manager, mock_bank_client):
    """
    Тест ошибки, когда для получения счетов не предоставлен consent_id.
    """
    bank_names = ["vbank", "abank"]
    user_id = "test-user-1"

    with patch("app.mcp.services.get_bank_client", return_value=mock_bank_client):
        results = await mcp_service.get_all_accounts(bank_names, user_id)

        assert len(results) == 2
        for result in results:
            assert result.status == "failed"
            assert "требуется consent_id" in result.message
        
        # mock_auth_manager.get_access_token не должен вызываться в этом сценарии
        mock_auth_manager.get_access_token.assert_not_called()
        assert mock_bank_client.accounts.get_accounts.call_count == 0

@pytest.mark.asyncio
async def test_get_all_accounts_token_not_found(mcp_service, mock_auth_manager):
    """
    Тест сценария, когда токен доступа для банка не найден.
    """
    bank_names = ["vbank"]
    user_id = "test-user-1"
    consent_id = "mock_consent_id" # Добавляем consent_id, чтобы пройти проверку
    mock_auth_manager.get_access_token.side_effect = TokenFetchError(bank_name="vbank", details="Test error")

    results = await mcp_service.get_all_accounts(bank_names, user_id, consent_id)

    assert len(results) == 1
    result = results[0]
    assert result.bank_name == "vbank"
    assert result.status == "failed"
    assert "Не удалось получить токен доступа" in result.message
    assert result.error == "TOKEN_FETCH_ERROR"

@pytest.mark.asyncio
async def test_create_consent_success(mcp_service, mock_auth_manager, mock_bank_client):
    """
    Тест успешного создания согласия через MCP.
    """
    bank_name = "vbank"
    permissions = ["ReadAccountsDetail"]
    user_id = "test-user-1"
    consent_id = "mock-consent-id"

    with patch("app.mcp.services.get_bank_client", return_value=mock_bank_client):
        mock_bank_client.create_consent.return_value = consent_id

        result = await mcp_service.create_bank_consent(bank_name, permissions, user_id)

        assert result.bank_name == bank_name
        assert result.status == "success"
        assert result.data == consent_id
        mock_auth_manager.get_access_token.assert_called_once_with(mcp_service.db, bank_name)
        mock_bank_client.create_consent.assert_called_once_with("mock_access_token", permissions, user_id)

# --- Tests for API Endpoints --- 

def test_api_get_all_accounts_error(test_client):
    """
    Интеграционный тест получения счетов через API, ожидаем ошибку из-за отсутствия consent_id.
    """
    response = test_client.post(
        "/api/v1/mcp/accounts/all",
        json={"bank_names": ["vbank"], "user_id": "test-user-1"}
    )
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["status"] == "failed"
    assert "требуется consent_id" in results[0]["message"]

def test_api_create_consent_success(test_client, mock_bank_client):
    """
    Интеграционный тест успешного создания согласия через API эндпоинт.
    """
    consent_id = "mock-consent-id"
    with patch("app.mcp.services.get_bank_client", return_value=mock_bank_client):
        mock_bank_client.create_consent.return_value = consent_id

        response = test_client.post(
            "/api/v1/mcp/consents/create",
            json={
                "bank_name": "vbank",
                "permissions": ["ReadAccountsDetail"],
                "user_id": "test-user-1"
            }
        )
        assert response.status_code == 200
        result = response.json()
        assert result["bank_name"] == "vbank"
        assert result["status"] == "success"
        assert result["data"] == consent_id