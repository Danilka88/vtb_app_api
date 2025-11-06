import pytest
from fastapi.testclient import TestClient

# Используем USER_ID из настроек для тестов
USER_ID = "team042-1"

class TestVBankAccountWorkflow:
    """
    Класс, объединяющий тесты для API счетов VBank.
    """
    account_id: str | None = "acc-1511"  # Используем известный ID для тестов
    consent_id: str | None = None

    def test_0_init_bank_tokens(self, client: TestClient):
        """
        Шаг 0: Инициализация банковских токенов.
        """
        print("\n--- Шаг 0: Инициализация банковских токенов (VBank Accounts) ---")
        response = client.post("/api/v1/auth/init-bank-tokens")
        assert response.status_code == 200, f"Ошибка при инициализации банк-токенов: {response.text}"
        print("Банк-токены успешно инициализированы.")

    def test_1_create_and_get_consent(self, client: TestClient):
        """
        Шаг 1: Создание и получение согласия на доступ к счетам.
        """
        print("\n--- Шаг 1: Создание и получение согласия (VBank Accounts) ---")
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

    def test_2_get_account_details(self, client: TestClient):
        """
        Шаг 2: Получение деталей счета.
        """
        assert self.consent_id, "Consent ID не был создан"
        assert self.account_id, "Account ID не установлен"
        print("\n--- Шаг 2: Получение деталей счета (VBank Accounts) ---")
        response = client.get(
            f"/api/v1/data/accounts/{self.account_id}",
            params={"bank_name": "vbank", "consent_id": self.consent_id, "user_id": USER_ID}
        )
        assert response.status_code == 200, f"Ошибка при получении деталей счета: {response.text}"
        assert "account" in response.json()
        assert response.json()["account"][0]["accountId"] == self.account_id
        print(f"Детали счета {self.account_id} успешно получены.")

    def test_3_get_account_balances(self, client: TestClient):
        """
        Шаг 3: Получение баланса счета.
        """
        assert self.consent_id, "Consent ID не был создан"
        assert self.account_id, "Account ID не установлен"
        print("\n--- Шаг 3: Получение баланса счета (VBank Accounts) ---")
        request_data = {
            "bank_name": "vbank",
            "consent_id": self.consent_id,
            "user_id": USER_ID
        }
        response = client.post(f"/api/v1/data/accounts/{self.account_id}/balances", json=request_data)
        assert response.status_code == 200, f"Ошибка при получении баланса: {response.text}"
        assert "balances" in response.json()
        print(f"Баланс счета {self.account_id} успешно получен.")

    def test_4_revoke_consent(self, client: TestClient):
        """
        Шаг 4: Отзыв согласия после тестов.
        """
        assert self.consent_id, "Consent ID не был создан"
        print(f"\n--- Шаг 4: Отзыв согласия {self.consent_id} (VBank Accounts) ---")
        response_revoke = client.delete(f"/api/v1/auth/consents/{self.consent_id}?bank_name=vbank&user_id={USER_ID}")
        assert response_revoke.status_code == 200, f"Ошибка при отзыве согласия: {response_revoke.text}"
        print(f"Согласие {self.consent_id} успешно отозвано.")

# Пропущенные тесты, которые требуют другой аутентификации
@pytest.mark.skip(reason="POST /accounts требует client_token, который не используется в этих тестах")
def test_create_account(): pass

@pytest.mark.skip(reason="PUT /accounts/{id}/status требует client_token")
def test_update_account_status(): pass

@pytest.mark.skip(reason="PUT /accounts/{id}/close требует client_token")
def test_close_account(): pass