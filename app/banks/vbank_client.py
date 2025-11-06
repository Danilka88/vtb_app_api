import httpx
from datetime import datetime, timedelta, timezone

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
        print(f"DEBUG: Запрос банк-токена для VBank. client_id: {self.client_id}")
        response = await self._async_client.post(
            f"{self.api_url}/auth/bank-token",
            params={"client_id": self.client_id, "client_secret": self.client_secret}
        )
        response.raise_for_status()  # Вызывает исключение для плохих статусов HTTP
        token_data = response.json()
        print(f"DEBUG: Получен банк-токен для VBank: {token_data}")
        return token_data

    async def create_consent(self, access_token: str, permissions: list[str], user_id: str) -> str:
        # DeprecationWarning: datetime.datetime.utcnow() is deprecated. Use datetime.datetime.now(datetime.UTC).
        """
        Создает согласие на доступ к данным счета для VBank.
        Этот метод обрабатывает только согласия, связанные с доступом к данным (не платежные).
        Примечание: Поля expiration_date, transaction_from_date, transaction_to_date временно не используются
        в запросе к VBank API для отладки.
        """
        now = datetime.now(timezone.utc)
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
                "client_id": user_id
            }
        )
        response.raise_for_status()
        return response.json()["consent_id"]

    async def create_payment_consent(self, access_token: str, permissions: list[str], user_id: str, requesting_bank: str, debtor_account_id: str, amount: str, currency: str = "RUB") -> str:
        """
        Создает платежное согласие для VBank.
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

    async def get_consent(self, access_token: str, consent_id: str, user_id: str) -> dict:
        """
        Получает информацию о согласии по его ID из VBank.
        """
        response = await self._async_client.get(
            f"{self.api_url}/account-consents/{consent_id}",
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-Requesting-Bank": settings.CLIENT_ID
            },
            params={"client_id": user_id}
        )
        response.raise_for_status()
        return response.json()

    async def get_payment_consent(self, access_token: str, consent_id: str, user_id: str) -> dict:
        """
        Получает информацию о платежном согласии по его ID из VBank.
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
        Отзывает платежное согласие по его ID из VBank.
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

    async def revoke_consent(self, access_token: str, consent_id: str, user_id: str) -> dict:
        """
        Отзывает согласие по его ID из VBank.
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
