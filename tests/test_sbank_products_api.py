
import pytest
from fastapi.testclient import TestClient

# Используем USER_ID из настроек для тестов
USER_ID = "team042-1"

@pytest.mark.skip(reason="SBank требует ручного подтверждения согласий, что делает автоматическое тестирование невозможным для большинства операций с продуктами.")
class TestSBankProductWorkflow:
    """
    Класс, объединяющий тесты для сквозного сценария 
    взаимодействия с API продуктов SBank.
    """
    product_id: str | None = None
    product_agreement_consent_id: str | None = None
    product_agreement_id: str | None = None

    def test_0_init_bank_tokens(self, client: TestClient):
        """
        Шаг 0: Инициализация банковских токенов.
        """
        print("\n--- Шаг 0: Инициализация банковских токенов (SBank Products) ---")
        response = client.post("/api/v1/auth/init-bank-tokens")
        assert response.status_code == 200, f"Ошибка при инициализации банк-токенов: {response.text}"
        print("Банк-токены успешно инициализированы.")

    def test_1_get_product_catalog(self, client: TestClient):
        """
        Шаг 1: Получение каталога продуктов и выбор одного продукта.
        """
        print("\n--- Шаг 1: Получение каталога продуктов (SBank Products) ---")
        response = client.get("/api/v1/products/products", params={"bank_name": "sbank"})
        assert response.status_code == 200, f"Ошибка при получении каталога продуктов: {response.text}"
        products = response.json()
        assert products, "Каталог продуктов пуст"
        TestSBankProductWorkflow.product_id = products[0]["productId"]
        assert self.product_id, "ID продукта не найден в каталоге"
        print(f"Каталог продуктов получен. Выбран продукт ID: {self.product_id}")

    def test_2_create_product_agreement_consent(self, client: TestClient):
        pass

    def test_3_get_product_agreement_consent(self, client: TestClient):
        pass

    def test_4_create_product_agreement(self, client: TestClient):
        pass

    def test_5_get_product_agreements(self, client: TestClient):
        pass

    def test_6_get_product_agreement_details(self, client: TestClient):
        pass

    def test_7_close_product_agreement(self, client: TestClient):
        pass

    def test_8_revoke_product_agreement_consent(self, client: TestClient):
        pass

