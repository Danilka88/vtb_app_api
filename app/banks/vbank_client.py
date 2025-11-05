import httpx
from datetime import datetime, timedelta

from app.banks.base_client import BaseBankClient
from app.core.config import settings
from app.banks.services.accounts.vbank import VBankAccountsService
from app.banks.services.payments.vbank import VBankPaymentsService


class VBankClient(BaseBankClient):
    """
    Клиент для взаимодействия с API VBank.
    Реализует специфические методы для получения токенов, создания согласий
    и предоставляет доступ к сервисам счетов и платежей VBank.
    """
    def __init__(self, client_id: str, client_secret: str, api_url: str):
        super().__init__(client_id, client_secret, api_url)
        # Инициализация специфичных для VBank сервисов
        self._accounts_service = VBankAccountsService(self)
        self._payments_service = VBankPaymentsService(self)

    async def get_bank_token(self) -> dict:
        """
        Получает банк-токен для VBank.
        """
        response = await self._async_client.post(
            f"{self.api_url}/auth/bank-token",
            params={"client_id": self.client_id, "client_secret": self.client_secret}
        )
        response.raise_for_status()  # Вызывает исключение для плохих статусов HTTP
        return response.json()

    async def create_consent(self, access_token: str, permissions: list[str], user_id: str) -> str:
        """
        Создает согласие на доступ к данным счета для VBank.
        Этот метод обрабатывает только согласия, связанные с доступом к данным (не платежные).
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

    async def create_payment_consent(self, access_token: str, permissions: list[str], user_id: str, requesting_bank: str, debtor_account_id: str, amount: str) -> str:
        """
        Создает платежное согласие для VBank.
        """
        now = datetime.utcnow()
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
                "amount": amount
            }
        )
        response.raise_for_status()
        return response.json()["consent_id"]

    @property
    def accounts(self) -> VBankAccountsService:
        """
        Возвращает сервис для работы со счетами VBank.
        """
        return self._accounts_service

    @property
    def payments(self) -> VBankPaymentsService:
        """
        Возвращает сервис для работы с платежами VBank.
        """ 
        return self._payments_service
