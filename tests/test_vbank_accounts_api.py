import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock

# Используем USER_ID из настроек для тестов
USER_ID = "team042-1"

@pytest.fixture(autouse=True)
def mock_httpx_client(mocker):
    """
    Автоматическая фикстура для мокирования httpx.AsyncClient.
    Это предотвратит реальные сетевые вызовы во всех тестах этого модуля.
    """
    mock_client = AsyncMock()
    mocker.patch("httpx.AsyncClient", return_value=mock_client)
    return mock_client

class TestVBankAccountWorkflow:
    """
    Класс, объединяющий тесты для API счетов VBank.
    Теперь тесты не зависят от сети.
    """
    account_id: str | None = "acc-1511"
    consent_id: str | None = None

    def test_1_create_and_get_consent(self, client: TestClient, mock_httpx_client: AsyncMock):
        """
        Шаг 1: Создание и получение согласия на доступ к счетам.
        """
        print("\n--- Шаг 1: Создание и получение согласия (VBank Accounts) ---")
        
        # Настраиваем мок для этого теста
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"consent_id": "mock_consent_id_123"}
        mock_httpx_client.post.return_value = mock_response

        consent_request = {
            "bank_name": "vbank",
            "user_id": USER_ID,
            "permissions": ["ReadAccountsDetail", "ReadBalances"]
        }
        response_create = client.post("/api/v1/auth/create-consent", json=consent_request)
        
        assert response_create.status_code == 200, f"Ошибка при создании согласия: {response_create.text}"
        TestVBankAccountWorkflow.consent_id = response_create.json().get("consent_id")
        assert self.consent_id, "Consent ID не найден в ответе"
        print(f"Согласие успешно создано. Consent ID: {self.consent_id}")

    def test_2_get_account_details(self, client: TestClient, mock_httpx_client: AsyncMock):
        """
        Шаг 2: Получение деталей счета.
        """
        assert self.consent_id, "Consent ID не был создан"
        assert self.account_id, "Account ID не установлен"
        print("\n--- Шаг 2: Получение деталей счета (VBank Accounts) ---")

        # Настраиваем мок для этого теста
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "account": [{"accountId": self.account_id, "currency": "RUB", "accountType": "DEBIT"}]
            }
        }
        mock_httpx_client.get.return_value = mock_response

        response = client.get(
            f"/api/v1/data/accounts/{self.account_id}",
            params={"bank_name": "vbank", "consent_id": self.consent_id, "user_id": USER_ID}
        )
        assert response.status_code == 200, f"Ошибка при получении деталей счета: {response.text}"
        account_details = response.json().get("account")
        assert account_details is not None, "Ответ не содержит ключ 'account'"
        assert isinstance(account_details, list), "Ключ 'account' должен содержать список"
        assert account_details[0]["accountId"] == self.account_id
        print(f"Детали счета {self.account_id} успешно получены.")

    def test_3_get_account_balances(self, client: TestClient, mock_httpx_client: AsyncMock):
        """
        Шаг 3: Получение баланса счета.
        """
        assert self.consent_id, "Consent ID не был создан"
        assert self.account_id, "Account ID не установлен"
        print("\n--- Шаг 3: Получение баланса счета (VBank Accounts) ---")

        # Настраиваем мок для этого теста
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "balance": [{"amount": {"amount": "1000.00", "currency": "RUB"}, "type": "interimAvailable"}]
            }
        }
        mock_httpx_client.post.return_value = mock_response

        request_data = {
            "bank_name": "vbank",
            "consent_id": self.consent_id,
            "user_id": USER_ID
        }
        response = client.post(f"/api/v1/data/accounts/{self.account_id}/balances", json=request_data)
        assert response.status_code == 200, f"Ошибка при получении баланса: {response.text}"
        assert "balances" in response.json()
        print(f"Баланс счета {self.account_id} успешно получен.")

    def test_4_revoke_consent(self, client: TestClient, mock_httpx_client: AsyncMock):
        """
        Шаг 4: Отзыв согласия после тестов.
        """
        assert self.consent_id, "Consent ID не был создан"
        print(f"\n--- Шаг 4: Отзыв согласия {self.consent_id} (VBank Accounts) ---")

        # Настраиваем мок для этого теста
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_response.text = ""
        mock_httpx_client.delete.return_value = mock_response

        response_revoke = client.delete(f"/api/v1/auth/consents/{self.consent_id}?bank_name=vbank&user_id={USER_ID}")
        assert response_revoke.status_code == 200, f"Ошибка при отзыве согласия: {response_revoke.text}"
        assert "Согласие успешно отозвано" in response_revoke.json()["message"]
        print(f"Согласие {self.consent_id} успешно отозвано.")

# Пропущенные тесты, которые требуют другой аутентификации
@pytest.mark.skip(reason="POST /accounts требует client_token, который не используется в этих тестах")
def test_create_account(): pass

@pytest.mark.skip(reason="PUT /accounts/{id}/status требует client_token")
def test_update_account_status(): pass

@pytest.mark.skip(reason="PUT /accounts/{id}/close требует client_token")
def test_close_account(): pass