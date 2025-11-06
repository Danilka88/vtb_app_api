import httpx
from datetime import datetime, timedelta, timezone

from app.banks.base_client import BaseBankClient
from app.core.config import settings


from app.banks.services.accounts.abank import ABankAccountsService
from app.banks.services.payments.abank import ABankPaymentsService


class ABankClient(BaseBankClient):
    """
    Клиент для взаимодействия с API ABank.
    Реализует специфические методы для получения токенов и создания согласий.
    """
    def __init__(self, client_id: str, client_secret: str, api_url: str):
        super().__init__(client_id, client_secret, api_url)
        self._accounts_service = ABankAccountsService(self)
        self._payments_service = ABankPaymentsService(self)

    async def get_bank_token(self) -> dict:
        """
        Получает банк-токен для ABank.
        """
        response = await self._async_client.post(
            f"{self.api_url}/auth/bank-token",
            params={"client_id": self.client_id, "client_secret": self.client_secret}
        )
        response.raise_for_status()
        return response.json()

    async def create_consent(self, access_token: str, permissions: list[str], user_id: str) -> str:
        """
        Создает согласие на доступ к данным счета для ABank.
        """
        now = datetime.now(timezone.utc)
        expiration_date = (now + timedelta(days=365)).isoformat(timespec='seconds') + 'Z'
        transaction_from_date = (now - timedelta(days=365)).isoformat(timespec='seconds') + 'Z'
        transaction_to_date = now.isoformat(timespec='seconds') + 'Z'

        response = await self._async_client.post(
            f"{self.api_url}/account-consents/request",
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-Requesting-Bank": settings.CLIENT_ID,
                "Content-Type": "application/json"
            },
            json={
                "permissions": permissions,
                "expiration_date": expiration_date,
                "transaction_from_date": transaction_from_date,
                "transaction_to_date": transaction_to_date,
                "client_id": user_id
            }
        )
        response.raise_for_status()
        return response.json()["consent_id"]

    @property
    def accounts(self) -> ABankAccountsService:
        """
        Возвращает сервис для работы со счетами ABank.
        """
        return self._accounts_service

    @property
    def payments(self) -> ABankPaymentsService:
        """
        Возвращает сервис для работы с платежами ABank.
        """
        return self._payments_service

    async def create_payment_consent(self, access_token: str, permissions: list[str], user_id: str, requesting_bank: str, debtor_account_id: str, amount: str, currency: str = "RUB") -> str:
        """
        Создает платежное согласие для ABank.
        """
        now = datetime.now(timezone.utc)
        expiration_date = (now + timedelta(days=365)).isoformat(timespec='seconds') + 'Z'

        response = await self._async_client.post(
            f"{self.api_url}/payment-consents/request",
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-Requesting-Bank": requesting_bank,
                "Content-Type": "application/json"
            },
            json={
                "permissions": permissions,
                "expiration_date": expiration_date,
                "client_id": user_id,
                "requesting_bank": requesting_bank,
                "debtor_account": debtor_account_id,
                "amount": amount,
                "currency": currency
            }
        )
        response.raise_for_status()
        return response.json()["consent_id"]

    async def get_payment_consent(self, access_token: str, consent_id: str, user_id: str) -> dict:
        """
        Получает информацию о платежном согласии по его ID из ABank.
        """
        response = await self._async_client.get(
            f"{self.api_url}/payment-consents/{consent_id}",
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-Requesting-Bank": settings.CLIENT_ID
            },
            params={"client_id": user_id}
        )
        response.raise_for_status()
        return response.json()

    async def revoke_payment_consent(self, access_token: str, consent_id: str, user_id: str) -> dict:
        """
        Отзывает платежное согласие по его ID из ABank.
        """
        response = await self._async_client.delete(
            f"{self.api_url}/payment-consents/{consent_id}",
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-Requesting-Bank": settings.CLIENT_ID
            },
            params={"client_id": user_id}
        )
        response.raise_for_status()

        if response.status_code == 204:
            return {"status": "success", "message": "Payment consent revoked successfully (no content)"}
        
        if not response.text:
            return {"status": "success", "message": "Payment consent revoked successfully (empty response)"}

        try:
            return response.json()
        except Exception:
            return {"status": "success", "message": "Payment consent revoked successfully (non-json response)"}

    async def get_consent(self, access_token: str, consent_id: str, user_id: str) -> dict:
        """
        Получает информацию о согласии по его ID из ABank.
        На данный момент не реализовано.
        """
        raise NotImplementedError("Метод get_consent не реализован для ABank.")

    async def revoke_consent(self, access_token: str, consent_id: str, user_id: str) -> dict:
        """
        Отзывает согласие по его ID из ABank.
        """
        response = await self._async_client.delete(
            f"{self.api_url}/account-consents/{consent_id}",
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-Requesting-Bank": settings.CLIENT_ID
            },
            params={"client_id": user_id}
        )
        response.raise_for_status() # Выбросит исключение для неуспешных статусов (4xx, 5xx)

        if response.status_code == 204:
            return {"status": "success", "message": "Consent revoked successfully (no content)"}
        
        if not response.text: # Если ответ пустой
            return {"status": "success", "message": "Consent revoked successfully (empty response)"}

        try:
            return response.json()
        except Exception: # Ловим любую ошибку при парсинге JSON
            # Если не удалось распарсить JSON, но статус был успешным (2xx, кроме 204)
            return {"status": "success", "message": "Consent revoked successfully (non-json response)"}
