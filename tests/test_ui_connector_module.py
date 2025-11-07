import pytest
from httpx import AsyncClient
from fastapi import FastAPI, Depends
from unittest.mock import AsyncMock, MagicMock

from app.ui_connector.router import router as ui_connector_router
from app.ui_connector.services import UIService, get_ui_service
from app.ui_connector import schemas
from app.mcp.schemas import BankOperationResponse
from app.mcp.services import MCPService
from app.schemas.account import Account as MCPSchemaAccount # Используем схему из MCP для мока
from app.schemas.payment import Transaction as MCPSchemaTransaction # Используем схему из MCP для мока


# --- Моковые данные ---
MOCK_ACCOUNTS = [
    MCPSchemaAccount(
        account_id="acc1",
        bank_name="VBank",
        account_name="Checking",
        account_type="debit",
        balance=1000.0,
        currency="RUB",
        status="active",
        last_four="1234",
        brand_color="#0033A0"
    ),
    MCPSchemaAccount(
        account_id="acc2",
        bank_name="ABank",
        account_name="Savings",
        account_type="savings",
        balance=5000.0,
        currency="RUB",
        status="active",
        last_four="5678",
        brand_color="#EF3124"
    ),
]

MOCK_TRANSACTIONS = [
    MCPSchemaTransaction(
        transaction_id="tr1",
        bank_name="VBank",
        account_id="acc1",
        description="Groceries",
        amount=-150.0,
        currency="RUB",
        type="expense",
        category="Food",
        date="2023-10-26T10:00:00Z"
    ),
    MCPSchemaTransaction(
        transaction_id="tr2",
        bank_name="VBank",
        account_id="acc1",
        description="Salary",
        amount=1000.0,
        currency="RUB",
        type="income",
        category="Salary",
        date="2023-10-25T10:00:00Z"
    ),
    MCPSchemaTransaction(
        transaction_id="tr3",
        bank_name="ABank",
        account_id="acc2",
        description="Rent",
        amount=-1000.0,
        currency="RUB",
        type="expense",
        category="Housing",
        date="2023-10-24T10:00:00Z"
    ),
    MCPSchemaTransaction(
        transaction_id="tr4",
        bank_name="VBank",
        account_id="acc1",
        description="Coffee",
        amount=-50.0,
        currency="RUB",
        type="expense",
        category="Food",
        date="2023-10-23T10:00:00Z"
    ),
    MCPSchemaTransaction(
        transaction_id="tr5",
        bank_name="VBank",
        account_id="acc1",
        description="Books",
        amount=-200.0,
        currency="RUB",
        type="expense",
        category="Education",
        date="2023-10-22T10:00:00Z"
    ),
    MCPSchemaTransaction(
        transaction_id="tr6",
        bank_name="VBank",
        account_id="acc1",
        description="Transfer",
        amount=-300.0,
        currency="RUB",
        type="expense",
        category="Переводы",
        date="2023-10-21T10:00:00Z"
    ),
]

# --- Тесты для UIService ---

@pytest.fixture
def mock_mcp_service():
    """Фикстура для мока MCPService."""
    mcp_service = AsyncMock(spec=MCPService)
    
    # Мокаем get_all_accounts, чтобы он возвращал BankOperationResponse с данными в виде списка словарей
    mock_account_responses = [
        BankOperationResponse(
            bank_name=acc.bank_name,
            status="success",
            data=[acc.model_dump()] # Преобразуем Pydantic модель в словарь
        ) for acc in MOCK_ACCOUNTS
    ]
    mcp_service.get_all_accounts.return_value = mock_account_responses
    
    # Мокаем get_transactions_for_account, чтобы он возвращал список словарей
    # только для первого счета, для остальных - пустой список.
    # Это имитирует, что транзакции привязаны к конкретному счету.
    def get_transactions_side_effect(bank_name, user_id, consent_id, account_id):
        if account_id == MOCK_ACCOUNTS[0].account_id:
            return [t.model_dump() for t in MOCK_TRANSACTIONS]
        return []
    mcp_service.get_transactions_for_account.side_effect = get_transactions_side_effect
    
    return mcp_service

@pytest.mark.asyncio
async def test_get_dashboard_data_service(mock_mcp_service):
    """
    Тестирование метода get_dashboard_data в UIService.
    """
    ui_service = UIService(mcp_service=mock_mcp_service)
    
    user_id = "test_user"
    consent_id = "test_consent"

    dashboard_data = await ui_service.get_dashboard_data(user_id, consent_id)

    # Проверяем, что MCPService был вызван с правильными аргументами
    mock_mcp_service.get_all_accounts.assert_called_once_with(
        bank_names=["VBank", "ABank", "SBank"], user_id=user_id, consent_id=consent_id
    )
    # Проверяем, что get_transactions_for_account был вызван (хотя бы один раз)
    mock_mcp_service.get_transactions_for_account.assert_called()

    # Проверяем общий капитал
    expected_net_worth = sum(acc.balance for acc in MOCK_ACCOUNTS)
    assert dashboard_data.net_worth == expected_net_worth

    # Проверяем количество счетов
    assert len(dashboard_data.accounts) == len(MOCK_ACCOUNTS)
    assert dashboard_data.accounts[0].account_id == MOCK_ACCOUNTS[0].account_id

    # Проверяем последние транзакции (должно быть 5)
    assert len(dashboard_data.recent_transactions) == 5
    assert dashboard_data.recent_transactions[0].transaction_id == MOCK_TRANSACTIONS[0].transaction_id

    # Проверяем данные для диаграммы трат
    expected_spending_data = {
        "Food": 200.0, # 150 + 50
        "Housing": 1000.0,
        "Education": 200.0,
    }
    assert dashboard_data.spending_chart_data == expected_spending_data

    # Проверяем финансовые цели (пока заглушка)
    assert dashboard_data.financial_goals == []

# --- Тесты для API-эндпоинта ---

@pytest.fixture(name="app")
def fastapi_app():
    """Фикстура для тестового FastAPI приложения."""
    test_app = FastAPI()
    test_app.include_router(ui_connector_router, prefix="/api/v1/ui")
    return test_app

@pytest.fixture
def mock_ui_service():
    """Фикстура для мока UIService."""
    ui_service = AsyncMock(spec=UIService)
    
    # Мокаем возвращаемое значение get_dashboard_data
    mock_dashboard_data = schemas.DashboardData(
        net_worth=6000.0,
        accounts=[
            schemas.Account(
                account_id="acc1", bank_name="VBank", account_name="Checking", account_type="debit",
                balance=1000.0, currency="RUB", status="active", last_four="1234", brand_color="#0033A0"
            )
        ],
        spending_chart_data={"Food": 200.0},
        recent_transactions=[
            schemas.Transaction(
                transaction_id="tr1", bank_name="VBank", account_id="acc1", description="Groceries",
                amount=-150.0, currency="RUB", type="expense", category="Food", date="2023-10-26T10:00:00Z"
            )
        ],
        financial_goals=[]
    )
    ui_service.get_dashboard_data.return_value = mock_dashboard_data
    return ui_service

# Переопределяем зависимость get_ui_service для тестов
# Это должно быть сделано после инициализации app
# app.dependency_overrides[get_ui_service] = lambda: mock_ui_service


from fastapi.testclient import TestClient

# ... (остальной код) ...

@pytest.mark.asyncio
async def test_post_dashboard_endpoint(app: FastAPI, mock_ui_service):
    """
    Тестирование эндпоинта POST /api/v1/ui/dashboard.
    """
    app.dependency_overrides[get_ui_service] = lambda: mock_ui_service
    client = TestClient(app) # Используем TestClient
    
    response = client.post(
        "/api/v1/ui/dashboard",
        json={"user_id": "test_user", "consent_id": "test_consent"}
    )
    app.dependency_overrides = {} # Очищаем переопределения после теста

    assert response.status_code == 200
    data = response.json()

    # Проверяем структуру и часть данных
    assert data["net_worth"] == 6000.0
    assert len(data["accounts"]) == 1
    assert data["accounts"][0]["account_id"] == "acc1"
    assert data["spending_chart_data"] == {"Food": 200.0}
    assert len(data["recent_transactions"]) == 1
    assert data["recent_transactions"][0]["transaction_id"] == "tr1"
    assert data["financial_goals"] == []

    # Проверяем, что метод сервиса был вызван
    mock_ui_service.get_dashboard_data.assert_called_once_with(user_id="test_user", consent_id="test_consent")
