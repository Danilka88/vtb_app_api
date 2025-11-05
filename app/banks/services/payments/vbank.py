import httpx
from typing import Optional

from app.banks.services.payments.base import BasePaymentsService, PaymentInitiationRequest, VRPPaymentRequest, VRPConsentRequest
from app.core.config import settings


class VBankPaymentsService(BasePaymentsService):
    """
    Сервис для работы с платежами в VBank.
    Реализует специфическую логику взаимодействия с API VBank для создания
    и получения статуса разовых платежей, а также для работы с VRP.
    """

    async def create_payment(self, access_token: str, payment_request: PaymentInitiationRequest, consent_id: Optional[str] = None) -> dict:
        """
        Инициирует разовый платеж через API VBank.
        Для успешного выполнения платежа требуется действующее платежное согласие.
        
        - `access_token`: Токен доступа для авторизации.
        - `payment_request`: Объект с данными для инициации платежа.
        - `consent_id`: Идентификатор платежного согласия. Обязателен.
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Requesting-Bank": settings.CLIENT_ID,
            "Content-Type": "application/json",
            "x-fapi-financial-id": "vbank",
            "x-idempotency-key": payment_request.data.initiation.instruction_identification
        }
        if consent_id:
            headers["X-Payment-Consent-Id"] = consent_id

        response = await self.main_client._async_client.post(
            f"{self.api_url}/payments",
            headers=headers,
            json=payment_request.model_dump(exclude_none=True),
            params={"client_id": self.main_client.client_id} # Передаем client_id как параметр запроса
        )
        response.raise_for_status()
        return response.json()

    async def get_payment_status(self, access_token: str, payment_id: str, client_id: str) -> dict:
        """
        Получает статус ранее созданного платежа из VBank.

        - `access_token`: Токен доступа для авторизации.
        - `payment_id`: Идентификатор платежа.
        - `client_id`: Идентификатор клиента, для которого был создан платеж.
        """
        response = await self.main_client._async_client.get(
            f"{self.api_url}/payments/{payment_id}",
            headers={
                "Authorization": f"Bearer {access_token}",
                "x-fapi-financial-id": "vbank"
            },
            params={"client_id": client_id} # Используем переданный client_id
        )
        response.raise_for_status()
        return response.json()

    async def create_vrp_consent(self, access_token: str, vrp_data: VRPConsentRequest) -> dict:
        """
        Создает согласие на периодические платежи (VRP) для VBank.

        - `access_token`: Токен доступа для авторизации.
        - `vrp_data`: Данные для создания VRP согласия.
        """
        response = await self.main_client._async_client.post(
            f"{self.api_url}/vrp-consents",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            },
            json=vrp_data.model_dump(exclude_none=True) # Используем model_dump для Pydantic v2
        )
        response.raise_for_status()
        return response.json()

    async def get_vrp_consent(self, access_token: str, user_id: str, consent_id: str) -> dict:
        """
        Получает информацию о VRP согласии из VBank.

        - `access_token`: Токен доступа для авторизации.
        - `user_id`: Идентификатор пользователя.
        - `consent_id`: Идентификатор VRP согласия.
        """
        response = await self.main_client._async_client.get(
            f"{self.api_url}/vrp-consents/{consent_id}",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"client_id": user_id} # Добавлено client_id для полноты, если API требует
        )
        response.raise_for_status()
        return response.json()

    async def create_vrp_payment(self, access_token: str, consent_id: str, user_id: str, payment_data: VRPPaymentRequest) -> dict:
        """
        Инициирует платеж в рамках VRP согласия для VBank.

        - `access_token`: Токен доступа для авторизации.
        - `consent_id`: Идентификатор VRP согласия, в рамках которого производится платеж.
        - `user_id`: Идентификатор пользователя.
        - `payment_data`: Данные для VRP платежа.
        """
        response = await self.main_client._async_client.post(
            f"{self.api_url}/vrp-consents/{consent_id}/payments", # Используем consent_id в URL для VRP
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "x-idempotency-key": payment_data.data.instruction.instruction_identification
            },
            json=payment_data.model_dump(exclude_none=True),
            params={"client_id": user_id} # Возможно, API требует client_id
        )
        response.raise_for_status()
        return response.json()
