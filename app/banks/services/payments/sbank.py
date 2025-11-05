import httpx
from typing import Optional

from app.banks.services.payments.base import BasePaymentsService, PaymentInitiationRequest, VRPPaymentRequest, VRPConsentRequest
from app.core.config import settings


class SBankPaymentsService(BasePaymentsService):
    """
    Сервис для работы с платежами в SBank.
    Реализует специфическую логику взаимодействия с API SBank для создания
    и получения статуса разовых платежей, а также для работы с VRP.
    """

    async def create_payment(self, access_token: str, payment_request: PaymentInitiationRequest, consent_id: Optional[str] = None) -> dict:
        """
        Инициирует разовый платеж через API SBank.
        Для успешного выполнения платежа требуется действующее платежное согласие.
        
        - `access_token`: Токен доступа для авторизации.
        - `payment_request`: Объект с данными для инициации платежа.
        - `consent_id`: Идентификатор платежного согласия. Обязателен.
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Requesting-Bank": settings.CLIENT_ID,
            "Content-Type": "application/json",
            "x-fapi-financial-id": "sbank",
            "x-idempotency-key": payment_request.data.initiation.instruction_identification
        }
        if consent_id:
            headers["X-Payment-Consent-Id"] = consent_id

        response = await self.client.post(
            f"{self.api_url}/payments",
            headers=headers,
            json=payment_request.model_dump(exclude_none=True),
            params={"client_id": self.main_client.client_id}
        )
        response.raise_for_status()
        return response.json()

    async def get_payment_status(self, access_token: str, payment_id: str, client_id: str) -> dict:
        """
        Получает статус ранее созданного платежа из SBank.

        - `access_token`: Токен доступа для авторизации.
        - `payment_id`: Идентификатор платежа.
        - `client_id`: Идентификатор клиента, для которого был создан платеж.
        """
        response = await self.client.get(
            f"{self.api_url}/payments/{payment_id}",
            headers={
                "Authorization": f"Bearer {access_token}",
                "x-fapi-financial-id": "sbank"
            },
            params={"client_id": client_id}
        )
        response.raise_for_status()
        return response.json()

    async def create_vrp_consent(self, access_token: str, user_id: str, vrp_data: VRPConsentRequest) -> dict:
        """
        Создает согласие на периодические платежи (VRP) для SBank.
        На данный момент не реализовано.
        """
        raise NotImplementedError("Метод create_vrp_consent не реализован для SBank")

    async def get_vrp_consent(self, access_token: str, user_id: str, consent_id: str) -> dict:
        """
        Получает информацию о VRP согласии из SBank.
        На данный момент не реализовано.
        """
        raise NotImplementedError("Метод get_vrp_consent не реализован для SBank")

    async def create_vrp_payment(self, access_token: str, consent_id: str, user_id: str, payment_data: VRPPaymentRequest) -> dict:
        """
        Инициирует платеж в рамках VRP согласия для SBank.
        На данный момент не реализовано.
        """
        raise NotImplementedError("Метод create_vrp_payment не реализован для SBank")
