import httpx
from datetime import datetime, timedelta

from app.banks.base_client import BaseBankClient
from app.core.config import settings


from app.banks.services.accounts.base import BaseAccountsService
from app.banks.services.payments.base import BasePaymentsService


class SBankClient(BaseBankClient):
    """
    Клиент для взаимодействия с API SBank.
    Реализует специфические методы для получения токенов и создания согласий.
    """
    async def get_bank_token(self) -> dict:
        """
        Получает банк-токен для SBank.
        """
        response = await self._async_client.post(
            f"{self.api_url}/auth/bank-token",
            params={"client_id": self.client_id, "client_secret": self.client_secret}
        )
        response.raise_for_status()
        return response.json()

    async def create_consent(self, access_token: str, permissions: list[str], user_id: str) -> str:
        """
        Создает согласие на доступ к данным счета для SBank.
        """
        now = datetime.utcnow()
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
    def accounts(self) -> BaseAccountsService:
        """
        Возвращает сервис для работы со счетами SBank.
        """
        raise NotImplementedError("Сервис счетов не реализован для SBank.")

    @property
    def payments(self) -> BasePaymentsService:
        """
        Возвращает сервис для работы с платежами SBank.
        """
        raise NotImplementedError("Сервис платежей не реализован для SBank.")
