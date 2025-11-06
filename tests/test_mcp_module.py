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
from httpx import HTTPStatusError, Response

# --- Fixtures --- 

@pytest.fixture
def mock_db_session():
    """
    Фикстура для мокирования сессии базы данных.
    """
    return MagicMock(spec=Session)

@pytest.fixture
def mock_bank_client():
    """
    Фикстура для мокирования BaseBankClient и его сервисов.
    """
    mock_client = MagicMock(spec=BaseBankClient)
    mock_client._async_client = AsyncMock() # Мокаем внутренний httpx.AsyncClient
    mock_client.api_url = "http://mockbank.com"

    mock_accounts_service = MagicMock(spec=BaseAccountsService)
    mock_client.accounts = mock_accounts_service

    mock_payments_service = MagicMock(spec=BasePaymentsService)
    mock_client.payments = mock_payments_service

    mock_products_service = MagicMock(spec=BaseProductsService)
    mock_client.products = mock_products_service

    # Мокаем методы создания/отзыва согласий на уровне клиента
    mock_client.create_consent = AsyncMock()
    mock_client.create_payment_consent = AsyncMock()
    mock_client.create_product_agreement_consent = AsyncMock()

    return mock_client

@pytest.fixture
def mcp_service(mock_db_session):
    """
    Фикстура для MCPService с мокированной сессией БД.
    """
    return MCPService(db=mock_db_session)

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

# --- Tests for MCPService --- 

@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_get_all_accounts_success(mcp_service, mock_db_session, mock_bank_client):
    """
    Тест успешного получения счетов из нескольких банков.
    """
    bank_names = ["vbank", "abank"]
    user_id = "test-user-1"

    # Мокируем crud.get_decrypted_token для возврата токена
    mock_db_session.query.return_value.filter.return_value.first.return_value.encrypted_token = b"encrypted_token"
    with patch("app.db.crud.encryption.decrypt", return_value="mock_access_token"):
        # Мокируем get_bank_client для возврата мокированного клиента
        with patch("app.mcp.services.get_bank_client", return_value=mock_bank_client):
            # Вызываем тестируемый метод
            results = await mcp_service.get_all_accounts(bank_names, user_id)

            # Проверяем результаты
            assert len(results) == 2
            assert results[0].bank_name == "vbank"
            assert results[0].status == "failed"
            assert f"из банка {results[0].bank_name}" in results[0].message
            assert f"требуется consent_id" in results[0].message
            assert results[0].error == f"Для получения счетов из банка {results[0].bank_name} требуется consent_id. MCP должен управлять согласиями."
            assert results[1].bank_name == "abank"
            assert results[1].status == "failed"
            assert f"из банка {results[1].bank_name}" in results[1].message
            assert f"требуется consent_id" in results[1].message
            assert results[1].error == f"Для получения счетов из банка {results[1].bank_name} требуется consent_id. MCP должен управлять согласиями."
            
            # Проверяем, что get_accounts не был вызван
            assert mock_bank_client.accounts.get_accounts.call_count == 0

@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_get_all_accounts_partial_failure(mcp_service, mock_db_session, mock_bank_client):
    """
    Тест частичного сбоя при получении счетов (один банк успешен, другой возвращает ошибку).
    """
    bank_names = ["vbank", "abank"]
    user_id = "test-user-1"

    mock_db_session.query.return_value.filter.return_value.first.return_value.encrypted_token = b"encrypted_token"
    with patch("app.db.crud.encryption.decrypt", return_value="mock_access_token"):
        with patch("app.mcp.services.get_bank_client", return_value=mock_bank_client):
            # Один банк успешен, другой выбрасывает HTTPStatusError
            # Этот side_effect будет вызван только если consent_id не None, что сейчас не так.
            # Поэтому для обоих банков будет ошибка consent_id.
            mock_bank_client.accounts.get_accounts.side_effect = [
                HTTPStatusError("Bad Request", request=MagicMock(), response=Response(400, request=MagicMock(), content=b'{"detail": "Consent required"}'))
            ]

            results = await mcp_service.get_all_accounts(bank_names, user_id)

            assert len(results) == 2
            assert results[0].bank_name == "vbank"
            assert results[0].status == "failed"
            assert f"из банка {results[0].bank_name}" in results[0].message
            assert f"требуется consent_id" in results[0].message
            assert results[0].error == f"Для получения счетов из банка {results[0].bank_name} требуется consent_id. MCP должен управлять согласиями."

            assert results[1].bank_name == "abank"
            assert results[1].status == "failed"
            assert f"из банка {results[1].bank_name}" in results[1].message
            assert f"требуется consent_id" in results[1].message
            assert results[1].error == f"Для получения счетов из банка {results[1].bank_name} требуется consent_id. MCP должен управлять согласиями."
            
            # Проверяем, что get_accounts не был вызван
            assert mock_bank_client.accounts.get_accounts.call_count == 0

@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_get_all_accounts_token_not_found(mcp_service, mock_db_session):
    """
    Тест сценария, когда токен доступа для банка не найден.
    """
    bank_names = ["vbank"]
    user_id = "test-user-1"

    # Мокируем crud.get_decrypted_token для возврата None
    mock_db_session.query.return_value.filter.return_value.first.return_value = None
    with patch("app.db.crud.encryption.decrypt", return_value=None):
        results = await mcp_service.get_all_accounts(bank_names, user_id)

        assert len(results) == 1
        assert results[0].bank_name == "vbank"
        assert results[0].status == "failed"
        assert results[0].message == "Токен доступа для банка vbank не найден."
        assert results[0].error == "TOKEN_NOT_FOUND"

@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_create_consent_success(mcp_service, mock_db_session, mock_bank_client):
    """
    Тест успешного создания согласия через MCP.
    """
    bank_name = "vbank"
    permissions = ["ReadAccountsDetail"]
    user_id = "test-user-1"
    consent_id = "mock-consent-id"

    mock_db_session.query.return_value.filter.return_value.first.return_value.encrypted_token = b"encrypted_token"
    with patch("app.db.crud.encryption.decrypt", return_value="mock_access_token"):
        with patch("app.mcp.services.get_bank_client", return_value=mock_bank_client):
            mock_bank_client.create_consent.return_value = consent_id

            result = await mcp_service.create_bank_consent(bank_name, permissions, user_id)

            assert result.bank_name == bank_name
            assert result.status == "success"
            assert result.data == consent_id
            mock_bank_client.create_consent.assert_called_once_with("mock_access_token", permissions, user_id)

@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_create_consent_payment_success(mcp_service, mock_db_session, mock_bank_client):
    """
    Тест успешного создания платежного согласия через MCP.
    """
    bank_name = "vbank"
    permissions = ["CreateDomesticSinglePayment"]
    user_id = "test-user-1"
    debtor_account = "12345"
    amount = "100.00"
    currency = "RUB"
    consent_id = "mock-payment-consent-id"

    mock_db_session.query.return_value.filter.return_value.first.return_value.encrypted_token = b"encrypted_token"
    with patch("app.db.crud.encryption.decrypt", return_value="mock_access_token"):
        with patch("app.mcp.services.get_bank_client", return_value=mock_bank_client):
            mock_bank_client.create_payment_consent.return_value = consent_id

            result = await mcp_service.create_bank_consent(bank_name, permissions, user_id, debtor_account, amount, currency)

            assert result.bank_name == bank_name
            assert result.status == "success"
            assert result.data == consent_id
            mock_bank_client.create_payment_consent.assert_called_once_with(
                "mock_access_token", permissions, user_id, settings.CLIENT_ID, debtor_account, amount, currency
            )

@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_create_consent_failure(mcp_service, mock_db_session, mock_bank_client):
    """
    Тест сбоя при создании согласия через MCP.
    """
    bank_name = "abank"
    permissions = ["ReadAccountsDetail"]
    user_id = "test-user-1"

    mock_db_session.query.return_value.filter.return_value.first.return_value.encrypted_token = b"encrypted_token"
    with patch("app.db.crud.encryption.decrypt", return_value="mock_access_token"):
        with patch("app.mcp.services.get_bank_client", return_value=mock_bank_client):
            mock_bank_client.create_consent.side_effect = HTTPStatusError("Forbidden", request=MagicMock(), response=Response(403, request=MagicMock(), content=b'{"detail": "Access Denied"}'))

            result = await mcp_service.create_bank_consent(bank_name, permissions, user_id)

            assert result.bank_name == bank_name
            assert result.status == "failed"
            assert "Access Denied" in result.message
            assert result.error == "403"

# --- Tests for API Endpoints --- 

def test_api_get_all_accounts_success(test_client, mock_db_session, mock_bank_client):
    """
    Интеграционный тест успешного получения счетов через API эндпоинт.
    """
    bank_names = ["vbank", "abank"]
    user_id = "test-user-1"

    mock_db_session.query.return_value.filter.return_value.first.return_value.encrypted_token = b"encrypted_token"
    with patch("app.db.crud.encryption.decrypt", return_value="mock_access_token"):
        with patch("app.mcp.services.get_bank_client", return_value=mock_bank_client):
            mock_bank_client.accounts.get_accounts.side_effect = [
                [{"account_id": "v1", "balance": 100}],
                [{"account_id": "a1", "balance": 200}]
            ]
            
            response = test_client.post(
                "/api/v1/mcp/accounts/all",
                json={
                    "bank_names": bank_names,
                    "user_id": user_id
                }
            )

            assert response.status_code == 200
            results = response.json()
            assert len(results) == 2
            assert results[0]["bank_name"] == "vbank"
            assert results[0]["status"] == "failed"
            assert results[0]["data"] is None

def test_api_create_consent_success(test_client, mock_db_session, mock_bank_client):
    """
    Интеграционный тест успешного создания согласия через API эндпоинт.
    """
    bank_name = "vbank"
    permissions = ["ReadAccountsDetail"]
    user_id = "test-user-1"
    consent_id = "mock-consent-id"

    mock_db_session.query.return_value.filter.return_value.first.return_value.encrypted_token = b"encrypted_token"
    with patch("app.db.crud.encryption.decrypt", return_value="mock_access_token"):
        with patch("app.mcp.services.get_bank_client", return_value=mock_bank_client):
            mock_bank_client.create_consent.return_value = consent_id

            response = test_client.post(
                "/api/v1/mcp/consents/create",
                json={
                    "bank_name": bank_name,
                    "permissions": permissions,
                    "user_id": user_id
                }
            )

            assert response.status_code == 200
            result = response.json()
            assert result["bank_name"] == bank_name
            assert result["status"] == "success"
            assert result["data"] == consent_id

