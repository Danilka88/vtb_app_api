import pytest
from fastapi.testclient import TestClient
from main import app
from app.core.config import settings

client = TestClient(app)

# Используем USER_ID для тестов ABank
USER_ID = "team042-2" # Используем другой user_id для ABank

# Глобальная переменная для хранения ID счета дебитора
DEBTOR_ACCOUNT_ID = None

def test_init_bank_tokens():
    """
    Тест для проверки инициализации банковских токенов для ABank.
    """
    print("\n--- Шаг 0: Инициализация банковских токенов для ABank ---")
    response = client.post("/api/v1/auth/init-bank-tokens")
    print(f"Статус ответа: {response.status_code}")
    print(f"Тело ответа: {response.json()}")
    assert response.status_code == 200, f"Ошибка при инициализации банковских токенов: {response.text}"
    print("Токены банков успешно инициализированы.")


def test_consent_management_flow():
    """
    Тест для проверки полного цикла управления согласиями (создание, получение, отзыв) для ABank.
    """
    print("\n--- Шаг 1: Управление согласиями для ABank ---")

    # 1. Создание согласия
    print("\n1.1. Создание согласия на доступ к счету для ABank...")
    consent_request = {
        "bank_name": "abank",
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
    assert consent_id, "Consent ID не найден в ответе"
    print(f"Согласие успешно создано. Consent ID: {consent_id}")

    # 2. Получение согласия по ID (ожидаем NotImplementedError)
    print(f"\n1.2. Получение деталей согласия по ID: {consent_id} для ABank (ожидаем 501)...")
    response_get = client.get(f"/api/v1/auth/consents/{consent_id}?bank_name=abank&user_id={USER_ID}")
    print(f"Статус ответа (получение): {response_get.status_code}")
    print(f"Тело ответа (получение): {response_get.json()}")
    assert response_get.status_code == 501, f"Ожидалась ошибка 501, получено: {response_get.status_code}"
    assert response_get.json().get("detail") == "Получение деталей согласия не реализовано для банка abank.", "Сообщение об ошибке не соответствует ожидаемому"
    print("Получение деталей согласия для ABank успешно вернуло 501 (NotImplementedError).")

    # 3. Отзыв согласия (ожидаем NotImplementedError)
    print(f"\n1.3. Отзыв согласия по ID: {consent_id} для ABank (ожидаем 501)...")
    response_revoke = client.delete(f"/api/v1/auth/consents/{consent_id}?bank_name=abank&user_id={USER_ID}")
    print(f"Статус ответа (отзыв): {response_revoke.status_code}")
    assert response_revoke.json().get("detail") == "Отзыв согласия не реализован для банка abank.", "Сообщение об ошибке не соответствует ожидаемому"
    print("Отзыв согласия для ABank успешно вернул 501 (NotImplementedError).")


def test_get_debtor_account():
    """
    Тест для получения реального счета для списания для ABank.
    """
    global DEBTOR_ACCOUNT_ID
    print("\n--- Шаг 2: Получение реального счета для списания для ABank ---")

    # 1. Создание согласия на доступ к счетам
    print("\n2.1. Создание согласия на доступ к счетам для ABank...")
    consent_request = {
        "bank_name": "abank",
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
    assert consent_id, "Consent ID не найден в ответе"
    print(f"Согласие на доступ к счетам успешно создано. Consent ID: {consent_id}")

    # 2. Получение списка счетов
    print("\n2.2. Получение списка счетов для ABank...")
    accounts_request = {
        "bank_name": "abank",
        "consent_id": consent_id,
        "user_id": USER_ID
    }
    response_accounts = client.post("/api/v1/data/accounts", json=accounts_request)
    print(f"Статус ответа (получение счетов): {response_accounts.status_code}")
    print(f"Тело ответа (получение счетов): {response_accounts.json()}")
    assert response_accounts.status_code == 200, f"Ошибка при получении счетов: {response_accounts.text}"
    
    accounts = response_accounts.json().get("accounts")
    assert accounts, "Список счетов пуст"
    assert len(accounts) > 0, "Не найдено ни одного счета"

    # Выбираем первый счет как счет дебитора
    DEBTOR_ACCOUNT_ID = accounts[0].get("accountId")
    assert DEBTOR_ACCOUNT_ID, "accountId не найден в первом счете"
    print(f"Получен счет дебитора: {DEBTOR_ACCOUNT_ID}")

    # Отзыв согласия после использования
    print(f"\n2.3. Отзыв согласия на доступ к счетам по ID: {consent_id} для ABank...")
    response_revoke = client.delete(f"/api/v1/auth/consents/{consent_id}?bank_name=abank&user_id={USER_ID}")
    print(f"Статус ответа (отзыв согласия): {response_revoke.status_code}")
    print(f"Тело ответа (отзыв согласия): {response_revoke.json()}")
    assert response_revoke.status_code == 501, f"Ожидалась ошибка 501, получено: {response_revoke.status_code}"
    assert response_revoke.json().get("detail") == "Отзыв согласия не реализован для банка abank.", "Сообщение об ошибке не соответствует ожидаемому"
    print("Отзыв согласия для ABank успешно вернул 501 (NotImplementedError).")
