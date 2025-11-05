import pytest
from fastapi.testclient import TestClient
from main import app
from app.core.config import settings

client = TestClient(app)

# Используем USER_ID из настроек для тестов
USER_ID = "team042-1"

# Глобальные переменные для хранения ID счета и согласия
TEST_ACCOUNT_ID = "acc-sbank-1" # Изменено для SBank
TEST_CONSENT_ID = None

@pytest.fixture(scope="module")
def init_bank_tokens():
    """
    Фикстура для инициализации банковских токенов перед выполнением тестов модуля.
    """
    print("\n--- Инициализация банк-токенов для SBank ---")
    # Этот эндпоинт инициализирует токены для всех банков, включая SBank
    response = client.post("/api/v1/auth/init-bank-tokens")
    assert response.status_code == 200, f"Ошибка при инициализации банк-токенов: {response.text}"
    print("Банк-токены успешно инициализированы.")


@pytest.mark.skip(reason="POST /accounts требует client_token или другого механизма аутентификации, который пока не реализован.")
def test_create_account(init_bank_tokens): # Добавляем фикстуру как аргумент
    """
    Тест для создания нового счета.
    """
    global TEST_ACCOUNT_ID
    print("\n--- Тест: Создание счета для SBank ---")

    request_data = {
        "account_type": "Personal",
        "initial_balance": 1000.0
    }
    response = client.post("/api/v1/data/accounts", params={"bank_name": "sbank"}, json=request_data) # Изменено bank_name
    print(f"Статус ответа: {response.status_code}")
    print(f"Тело ответа: {response.json()}")
    assert response.status_code == 200, f"Ошибка при создании счета: {response.text}"
    assert "account" in response.json()
    assert "accountId" in response.json()["account"]
    TEST_ACCOUNT_ID = response.json()["account"]["accountId"]
    print(f"Счет успешно создан. Account ID: {TEST_ACCOUNT_ID}")


@pytest.mark.skip(reason="SBank API возвращает Internal Server Error при получении деталей счета.") # Причина может быть изменена
def test_get_account_details():
    """
    Тест для получения деталей счета.
    """
    global TEST_CONSENT_ID
    print("\n--- Тест: Получение деталей счета для SBank ---")

    # 1. Создание согласия на доступ к счетам
    print("\n1.1. Создание согласия на доступ к счетам для SBank...")
    consent_request = {
        "bank_name": "sbank", # Изменено bank_name
        "user_id": USER_ID,
        "permissions": [
            "ReadAccountsDetail",
            "ReadBalances"
        ]
    }
    response_create = client.post("/api/v1/auth/create-consent", json=consent_request)
    assert response_create.status_code == 200, f"Ошибка при создании согласия: {response_create.text}"
    TEST_CONSENT_ID = response_create.json().get("consent_id")
    assert TEST_CONSENT_ID, "Consent ID не найден в ответе"
    print(f"Согласие успешно создано. Consent ID: {TEST_CONSENT_ID}")

    # 2. Получение деталей счета
    response = client.get(
        f"/api/v1/data/accounts/{TEST_ACCOUNT_ID}",
        params={
            "bank_name": "sbank", # Изменено bank_name
            "consent_id": TEST_CONSENT_ID,
            "user_id": USER_ID
        }
    )
    print(f"Статус ответа: {response.status_code}")
    print(f"Тело ответа: {response.json()}")
    assert response.status_code == 200, f"Ошибка при получении деталей счета: {response.text}"
    assert "account" in response.json()
    assert response.json()["account"][0]["accountId"] == TEST_ACCOUNT_ID
    print(f"Детали счета {TEST_ACCOUNT_ID} успешно получены.")


@pytest.mark.skip(reason="PUT /accounts/{account_id}/status требует client_token или другого механизма аутентификации, который пока не реализован.")
def test_update_account_status():
    """
    Тест для изменения статуса счета.
    """
    print("\n--- Тест: Изменение статуса счета для SBank ---")
    assert TEST_ACCOUNT_ID is not None, "Счет не был создан в предыдущем тесте."

    request_data = {
        "bank_name": "sbank", # Изменено bank_name
        "user_id": USER_ID,
        "status": "Disabled"
    }
    response = client.put(f"/api/v1/data/accounts/{TEST_ACCOUNT_ID}/status", json=request_data)
    print(f"Статус ответа: {response.status_code}")
    print(f"Тело ответа: {response.json()}")
    assert response.status_code == 200, f"Ошибка при изменении статуса счета: {response.text}"
    assert "account" in response.json()
    assert response.json()["account"]["status"] == "Disabled"
    print(f"Статус счета {TEST_ACCOUNT_ID} успешно изменен на Disabled.")


@pytest.mark.skip(reason="PUT /accounts/{account_id}/close требует client_token или другого механизма аутентификации, который пока не реализован.")
def test_close_account():
    """
    Тест для закрытия счета.
    """
    print("\n--- Тест: Закрытие счета для SBank ---")
    assert TEST_ACCOUNT_ID is not None, "Счет не был создан в предыдущем тесте."

    request_data = {
        "bank_name": "sbank", # Изменено bank_name
        "user_id": USER_ID
    }
    response = client.put(f"/api/v1/data/accounts/{TEST_ACCOUNT_ID}/close", json=request_data)
    print(f"Статус ответа: {response.status_code}")
    print(f"Тело ответа: {response.json()}")
    assert response.status_code == 200, f"Ошибка при закрытии счета: {response.text}"
    assert "account" in response.json()
    assert response.json()["account"]["status"] == "Closed"
    print(f"Счет {TEST_ACCOUNT_ID} успешно закрыт.")


def test_revoke_consent_after_tests():
    """
    Отзыв согласия после выполнения всех тестов, если оно было создано.
    """
    if TEST_CONSENT_ID:
        print(f"\n--- Отзыв согласия {TEST_CONSENT_ID} для SBank ---")
        response_revoke = client.delete(f"/api/v1/auth/consents/{TEST_CONSENT_ID}?bank_name=sbank&user_id={USER_ID}") # Изменено bank_name
        print(f"Статус ответа (отзыв): {response_revoke.status_code}")
        print(f"Тело ответа (отзыв): {response_revoke.json()}")
        assert response_revoke.status_code == 200, f"Ошибка при отзыве согласия: {response_revoke.text}"
        print(f"Согласие {TEST_CONSENT_ID} успешно отозвано.")
