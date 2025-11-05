import pytest
from fastapi.testclient import TestClient
from main import app
from app.core.config import settings

client = TestClient(app)

# Используем USER_ID для тестов SBank
USER_ID = "team042-3" # Используем другой user_id для SBank

# Глобальная переменная для хранения ID счета дебитора
DEBTOR_ACCOUNT_ID = None

def test_init_bank_tokens():
    """
    Тест для проверки инициализации банковских токенов для SBank.
    """
    print("\n--- Шаг 0: Инициализация банковских токенов для SBank ---")
    response = client.post("/api/v1/auth/init-bank-tokens")
    print(f"Статус ответа: {response.status_code}")
    print(f"Тело ответа: {response.json()}")
    assert response.status_code == 200, f"Ошибка при инициализации банковских токенов: {response.text}"
    print("Токены банков успешно инициализированы.")


def test_consent_management_flow():
    """
    Тест для проверки полного цикла управления согласиями (создание, получение, отзыв) для SBank.
    """
    print("\n--- Шаг 1: Управление согласиями для SBank ---")

    # 1. Создание согласия
    print("\n1.1. Создание согласия на доступ к счету для SBank...")
    consent_request = {
        "bank_name": "sbank",
        "user_id": USER_ID,
        "permissions": [
            "ReadAccountsDetail",
            "ReadBalances"
        ]
    }
    response_create = client.post("/api/v1/auth/create-consent", json=consent_request)
    print(f"Статус ответа (создание): {response_create.status_code}")
    print(f"Тело ответа (создание): {response_create.json()}")
    assert response_create.status_code == 200, f"Ошибка при создании согласия: {response_create.text}"
    consent_id = response_create.json().get("consent_id")
    assert consent_id is None, "Consent ID должен быть None для SBank до ручного подтверждения"
    print("Согласие успешно создано, Consent ID ожидаемо None.")

    # 2. Получение согласия по ID (ожидаем ошибку, так как consent_id = None)
    print(f"\n1.2. Попытка получения деталей согласия по ID: {consent_id} для SBank (ожидаем ошибку)...")
    response_get = client.get(f"/api/v1/auth/consents/{consent_id}?bank_name=sbank&user_id={USER_ID}")
    print(f"Статус ответа (получение): {response_get.status_code}")
    print(f"Тело ответа (получение): {response_get.json()}")
    assert response_get.status_code == 404, f"Ожидалась ошибка 404, получено: {response_get.status_code}"
    assert "Consent not found" in response_get.json().get("detail") or "Согласие не найдено" in response_get.json().get("detail"), "Сообщение об ошибке не соответствует ожидаемому"
    print("Попытка получения деталей согласия для SBank успешно вернула 404 (Consent not found).")

    # 3. Отзыв согласия (ожидаем ошибку, так как consent_id = None)
    print(f"\n1.3. Попытка отзыва согласия по ID: {consent_id} для SBank (ожидаем ошибку)...")
    response_revoke = client.delete(f"/api/v1/auth/consents/{consent_id}?bank_name=sbank&user_id={USER_ID}")
    print(f"Статус ответа (отзыв): {response_revoke.status_code}")
    print(f"Тело ответа (отзыв): {response_revoke.json()}")
    assert response_revoke.status_code == 404, f"Ожидалась ошибка 404, получено: {response_revoke.status_code}"
    assert "Consent not found" in response_revoke.json().get("detail") or "Согласие не найдено" in response_revoke.json().get("detail"), "Сообщение об ошибке не соответствует ожидаемому"
    print("Попытка отзыва согласия для SBank успешно вернула 404 (Consent not found).")


def test_get_debtor_account():
    """
    Тест для получения реального счета для списания для SBank.
    """
    global DEBTOR_ACCOUNT_ID
    print("\n--- Шаг 2: Получение реального счета для списания для SBank ---")

    # 1. Создание согласия на доступ к счетам
    print("\n2.1. Создание согласия на доступ к счетам для SBank...")
    consent_request = {
        "bank_name": "sbank",
        "user_id": USER_ID,
        "permissions": [
            "ReadAccountsDetail",
            "ReadBalances"
        ]
    }
    response_create = client.post("/api/v1/auth/create-consent", json=consent_request)
    print(f"Статус ответа (создание согласия): {response_create.status_code}")
    print(f"Тело ответа (создание согласия): {response_create.json()}")
    assert response_create.status_code == 200, f"Ошибка при создании согласия: {response_create.text}"
    consent_id = response_create.json().get("consent_id")
    assert consent_id is None, "Consent ID должен быть None для SBank до ручного подтверждения"
    print("Согласие на доступ к счетам успешно создано, Consent ID ожидаемо None.")

    # 2. Получение списка счетов (ожидаем ошибку, так как consent_id = None)
    print("\n2.2. Попытка получения списка счетов для SBank (ожидаем ошибку)...")
    accounts_request = {
        "bank_name": "sbank",
        "consent_id": consent_id,
        "user_id": USER_ID
    }
    response_accounts = client.post("/api/v1/data/accounts", json=accounts_request)
    print(f"Статус ответа (получение счетов): {response_accounts.status_code}")
    print(f"Тело ответа (получение счетов): {response_accounts.json()}")
    assert response_accounts.status_code == 422, f"Ожидалась ошибка 422, получено: {response_accounts.status_code}"
    assert "Input should be a valid string" in response_accounts.json().get("detail")[0].get("msg"), "Сообщение об ошибке не соответствует ожидаемому"
    print("Попытка получения списка счетов для SBank успешно вернула 422 (Unprocessable Entity).")

    # Отзыв согласия после использования (ожидаем ошибку, так как consent_id = None)
    print(f"\n2.3. Попытка отзыва согласия на доступ к счетам по ID: {consent_id} для SBank (ожидаем ошибку)...")
    response_revoke = client.delete(f"/api/v1/auth/consents/{consent_id}?bank_name=sbank&user_id={USER_ID}")
    print(f"Статус ответа (отзыв согласия): {response_revoke.status_code}")
    print(f"Тело ответа (отзыв согласия): {response_revoke.json()}")
    assert response_revoke.status_code == 404, f"Ожидалась ошибка 404, получено: {response_revoke.status_code}"
    assert "Consent not found" in response_revoke.json().get("detail") or "Согласие не найдено" in response_revoke.json().get("detail"), "Сообщение об ошибке не соответствует ожидаемому"
    print("Попытка отзыва согласия для SBank успешно вернула 404 (Consent not found).")
