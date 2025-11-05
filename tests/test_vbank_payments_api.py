import pytest
import uuid
from fastapi.testclient import TestClient

from main import app
from app.core.config import settings

client = TestClient(app)

USER_ID = "team042-1"
CLIENT_ID = "team042"

@pytest.fixture(scope="module", autouse=True)
def init_bank_tokens():
    """Фикстура для инициализации банковских токенов перед запуском тестов."""
    # Убедимся, что в settings правильный client_id
    settings.CLIENT_ID = CLIENT_ID
    response = client.post("/api/v1/auth/init-bank-tokens")
    assert response.status_code == 200, f"Failed to init bank tokens: {response.text}"
    print("Bank tokens initialized.")

def test_vbank_full_payment_flow():
    """
    Полный интеграционный тест для проверки всего цикла платежа через VBank.
    """
    # --- Шаг 1: Создание СОГЛАСИЯ НА ДОСТУП К СЧЕТУ с правами на платеж ---
    print("\nStep 1: Creating ACCOUNT consent with payment permissions...")
    account_consent_request = {
        "bank_name": "vbank",
        "user_id": USER_ID,
        "permissions": [
            "ReadAccountsDetail",
            "ReadBalances"
        ]
    }
    response_acc_consent = client.post("/api/v1/auth/create-consent", json=account_consent_request)
    assert response_acc_consent.status_code == 200, f"Error creating account consent: {response_acc_consent.text}"
    consent_id = response_acc_consent.json().get("consent_id")
    assert consent_id, "Account Consent ID not found in response"
    print(f"Account consent created successfully. Consent ID: {consent_id}")

    # --- Шаг 2: Получение реального счета для списания ---
    print("\nStep 2: Fetching accounts to get a valid debtor account...")
    accounts_request = {
        "bank_name": "vbank",
        "consent_id": consent_id,
        "user_id": USER_ID
    }
    response_accounts = client.post("/api/v1/data/accounts", json=accounts_request)
    assert response_accounts.status_code == 200, f"Failed to fetch accounts: {response_accounts.text}"
    accounts = response_accounts.json().get("accounts")
    assert accounts and len(accounts) > 0, "No accounts found for the user"
    
    # Извлекаем данные из вложенной структуры
    nested_account_info = accounts[0].get("account")[0]
    debtor_account_id = nested_account_info.get("identification")
    debtor_account_scheme = nested_account_info.get("schemeName")
    
    assert debtor_account_id, "Could not find a valid debtor account ID from nested data"
    print(f"Using debtor account: {debtor_account_id}")

    # --- Шаг 3: Создание СОГЛАСИЯ НА ПЛАТЕЖ ---
    print("\nStep 3: Creating PAYMENT consent...")
    payment_consent_request = {
        "bank_name": "vbank",
        "user_id": USER_ID,
        "permissions": [
            "CreateDomesticSinglePayment"
        ],
                                "requesting_bank": CLIENT_ID,
                                "debtor_account": debtor_account_id,
                                "amount": "1.00"    }
    response_pay_consent = client.post("/api/v1/auth/create-consent", json=payment_consent_request)
    assert response_pay_consent.status_code == 200, f"Error creating payment consent: {response_pay_consent.text}"
    payment_consent_id = response_pay_consent.json().get("consent_id")
    assert payment_consent_id, "Payment Consent ID not found in response"
    print(f"Payment consent created successfully. Consent ID: {payment_consent_id}")

    # --- Шаг 4: Инициация платежа ---
    instruction_id = str(uuid.uuid4())
    end_to_end_id = str(uuid.uuid4())

    # Собираем тело запроса в точном соответствии с документацией (смешанный регистр)
    payment_request_body = {
        "data": {
            "initiation": {
                "InstructionIdentification": instruction_id,
                "EndToEndIdentification": end_to_end_id,
                "InstructedAmount": {
                    "amount": "1.00",
                    "currency": "RUB"
                },
                "DebtorAccount": {
                    "schemeName": debtor_account_scheme,
                    "identification": debtor_account_id
                },
                "CreditorAccount": {
                    "schemeName": "RU.CBR.PAN",
                    "identification": "40817810099910005423", # Случайный счет получателя
                    "name": "Test Recipient"
                }
            }
        },
        "risk": {}
    }
    print("\nStep 4: Initiating payment...")
    response_payment = client.post(
        f"/api/v1/payments/vbank/create",
        json=payment_request_body,
                    headers={
                        "X-Consent-Id": payment_consent_id
                    }    )
    assert response_payment.status_code == 200, f"Error creating payment: {response_payment.text}"
    payment_details = response_payment.json()["details"]
    payment_id = payment_details.get("paymentId") # Поле в PascalCase
    assert payment_id, "Payment ID not found in response"
    print(f"Payment initiated successfully. Payment ID: {payment_id}")

    # --- Шаг 5: Проверка статуса платежа ---
    print("\nStep 5: Checking payment status...")
    response_status = client.get(
        f"/api/v1/payments/vbank/{payment_id}/status?client_id={CLIENT_ID}"
    )
    assert response_status.status_code == 200, f"Error getting status: {response_status.text}"
    status_details = response_status.json()["details"]
    status = status_details.get("data", {}).get("status")
    assert status in ["AcceptedSettlementCompleted", "AcceptedSettlementInProgress", "Pending"], f"Unexpected payment status: {status}"
    print(f"Payment status is '{status}'. Test completed successfully!")
