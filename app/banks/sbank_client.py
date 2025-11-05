import httpx
from datetime import datetime, timedelta

from app.banks.base_client import BaseBankClient
from app.core.config import settings


from app.banks.services.accounts.sbank import SBankAccountsService
from app.banks.services.payments.sbank import SBankPaymentsService


class SBankClient(BaseBankClient):
    """
    Клиент для взаимодействия с API SBank.
    Реализует специфические методы для получения токенов и создания согласий.
    """
    def __init__(self, client_id: str, client_secret: str, api_url: str):
        super().__init__(client_id, client_secret, api_url)
        self._accounts_service = SBankAccountsService(self)
        self._payments_service = SBankPaymentsService(self)

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
    def accounts(self) -> SBankAccountsService:
        """
        Возвращает сервис для работы со счетами SBank.
        """
        return self._accounts_service

    @property
    def payments(self) -> SBankPaymentsService:
        """
        Возвращает сервис для работы с платежами SBank.
        """
        return self._payments_service

    async def get_consent(self, access_token: str, consent_id: str, user_id: str) -> dict:
        """
        Получает информацию о согласии по его ID из SBank.
        На данный момент не реализовано.
        """
        raise NotImplementedError("Метод get_consent не реализован для SBank.")

    async def revoke_consent(self, access_token: str, consent_id: str, user_id: str) -> dict:
        """
        Отзывает согласие по его ID из SBank.
        На данный момент не реализовано.
        """
        raise NotImplementedError("Метод revoke_consent не реализован для SBank.")
