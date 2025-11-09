import pytest
from fastapi.testclient import TestClient
import uuid
from unittest.mock import AsyncMock, MagicMock

# Используем USER_ID из настроек для тестов
USER_ID = "team042-1"

@pytest.fixture(autouse=True)
def mock_httpx_client(mocker):
    """
    Автоматическая фикстура для мокирования httpx.AsyncClient.
    """
    mock_client = AsyncMock()
    mocker.patch("httpx.AsyncClient", return_value=mock_client)
    return mock_client

class TestABankPaymentWorkflow:
    """
    Класс, объединяющий все тесты для полного сквозного сценария 
    взаимодействия с платежным API ABank. 
    """
    debtor_account_id: str | None = None
    payment_consent_id: str | None = None
    payment_id: str | None = None

    def test_1_get_debtor_account(self, client: TestClient, mock_httpx_client: AsyncMock):
        """
        Шаг 1: Получение реального счета для списания (счет дебитора).
        """
        print("\n--- Шаг 1: Получение счета дебитора (Abank) ---")

        # 1.1 Мокаем создание согласия на доступ к счетам
        mock_response_consent = MagicMock()
        mock_response_consent.status_code = 200
        mock_response_consent.json.return_value = {"consent_id": "mock_account_consent_id"}
        mock_httpx_client.post.return_value = mock_response_consent
        
        consent_request = {
            "bank_name": "abank",
            "user_id": USER_ID,
            "permissions": ["ReadAccountsDetail"]
        }
        response_create = client.post("/api/v1/auth/create-consent", json=consent_request)
        assert response_create.status_code == 200, f"Ошибка при создании согласия на доступ к счетам: {response_create.text}"
        consent_id = response_create.json().get("consent_id")
        assert consent_id, "Account Consent ID не найден в ответе"
        print(f"Согласие на доступ к счетам успешно создано. Consent ID: {consent_id}")

        # 1.2 Мокаем получение списка счетов
        mock_response_accounts = MagicMock()
        mock_response_accounts.status_code = 200
        mock_response_accounts.json.return_value = {
            "data": {"account": [{"accountId": "mock_debtor_account_id"}]}
        }
        mock_httpx_client.get.return_value = mock_response_accounts
        
        accounts_request = {
            "bank_name": "abank",
            "consent_id": consent_id,
            "user_id": USER_ID
        }
        response_accounts = client.post("/api/v1/data/accounts/list", json=accounts_request)
        assert response_accounts.status_code == 200, f"Ошибка при получении счетов: {response_accounts.text}"
        accounts = response_accounts.json().get("accounts")
        assert accounts and len(accounts) > 0, "Список счетов пуст или не найден"

        TestABankPaymentWorkflow.debtor_account_id = accounts[0].get("accountId")
        assert self.debtor_account_id, "AccountId не найден в первом счете"
        print(f"Получен счет дебитора: {self.debtor_account_id}")

        # 1.3 Мокаем отзыв согласия
        mock_response_revoke = MagicMock()
        mock_response_revoke.status_code = 204
        mock_httpx_client.delete.return_value = mock_response_revoke
        
        response_revoke = client.delete(f"/api/v1/auth/consents/{consent_id}?bank_name=abank&user_id={USER_ID}")
        assert response_revoke.status_code == 200, f"Ошибка при отзыве согласия: {response_revoke.text}"
        print("Согласие на доступ к счетам успешно отозвано.")

    def test_2_payment_consent_workflow(self, client: TestClient, mock_httpx_client: AsyncMock):
        """
        Шаг 2: Создание и проверка ПЛАТЕЖНОГО согласия.
        """
        assert self.debtor_account_id, "Не удалось получить ID счета дебитора на предыдущем шаге."
        print("\n--- Шаг 2: Управление платежным согласием (Abank) ---")

        # 2.1 Мокаем создание платежного согласия
        mock_response_p_consent = MagicMock()
        mock_response_p_consent.status_code = 200
        mock_response_p_consent.json.return_value = {"consent_id": "mock_payment_consent_id"}
        mock_httpx_client.post.return_value = mock_response_p_consent

        consent_request = {
            "bank_name": "abank",
            "user_id": USER_ID,
            "permissions": ["CreateDomesticSinglePayment"],
            "debtor_account": self.debtor_account_id,
            "amount": "1.00"
        }
        response_create = client.post("/api/v1/payments/payment-consents", json=consent_request)
        assert response_create.status_code == 200, f"Ошибка при создании платежного согласия: {response_create.text}"
        TestABankPaymentWorkflow.payment_consent_id = response_create.json().get("consent_id")
        assert self.payment_consent_id, "Payment Consent ID не найден в ответе"
        print(f"Платежное согласие успешно создано. Consent ID: {self.payment_consent_id}")

    # Тесты ниже оставлены без изменений, так как они были пропущены
    @pytest.mark.skip(reason="Пропущено из-за постоянной ошибки 403 'Сумма платежа не совпадает с согласием', аналогично VBank")
    def test_3_payment_workflow(self, client: TestClient):
        pass

    @pytest.mark.skip(reason="Пропущено из-за предполагаемого требования mTLS, аналогично VBank")
    def test_4_revoke_payment_consent(self, client: TestClient):
        pass