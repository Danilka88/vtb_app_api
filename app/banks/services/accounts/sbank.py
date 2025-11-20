import httpx

from app.banks.services.accounts.base import BaseAccountsService
from app.core.config import settings


class SBankAccountsService(BaseAccountsService):
    """
    Сервис для работы со счетами в SBank.
    Реализует специфическую логику взаимодействия с API SBank для получения
    информации о счетах, балансах и транзакциях.
    """

    async def get_accounts(self, access_token: str, consent_id: str, user_id: str) -> list[dict]:
        """
        Получает список счетов пользователя из SBank.
        Требует `access_token` и `consent_id` с разрешением `ReadAccountsDetail`.
        """
        response = await self.client.get(
            f"{self.api_url}/accounts",
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-Requesting-Bank": settings.CLIENT_ID,
                "X-Consent-Id": consent_id
            },
            params={"client_id": user_id}
        )
        response.raise_for_status()
        response_data = response.json()
        # Проверяем ожидаемую структуру ответа от API SBank
        if "data" not in response_data or "account" not in response_data["data"]:
            raise ValueError(f"Неожиданная структура ответа от SBank при получении счетов: {response_data}")
        return response_data["data"]["account"]

    async def get_account_balances(self, access_token: str, consent_id: str, user_id: str, account_id: str) -> dict:
        """
        Получает балансы для конкретного счета из SBank.
        Требует `access_token` и `consent_id` с разрешением `ReadBalances`.
        """
        response = await self.client.get(
            f"{self.api_url}/accounts/{account_id}/balances",
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-Requesting-Bank": settings.CLIENT_ID,
                "X-Consent-Id": consent_id
            },
            params={"client_id": user_id}
        )
        response.raise_for_status()
        response_data = response.json()
        # Проверяем ожидаемую структуру ответа от API SBank
        if "data" not in response_data or "balance" not in response_data["data"]:
            raise ValueError(f"Неожиданная структура ответа от SBank при получении балансов: {response_data}")
        return response_data["data"]["balance"]

    async def get_account_transactions(self, access_token: str, consent_id: str, user_id: str, account_id: str) -> list[dict]:
        """
        Получает историю транзакций для конкретного счета из SBank.
        Требует `access_token` и `consent_id` с разрешением `ReadTransactionsDetail`.
        """
        response = await self.client.get(
            f"{self.api_url}/accounts/{account_id}/transactions",
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-Requesting-Bank": settings.CLIENT_ID,
                "X-Consent-Id": consent_id
            },
            params={"client_id": user_id}
        )
        response.raise_for_status()
        response_data = response.json()
        # Проверяем ожидаемую структуру ответа от API SBank
        if "data" not in response_data or "transaction" not in response_data["data"]:
            raise ValueError(f"Неожиданная структура ответа от SBank при получении транзакций: {response_data}")
        return response_data["data"]["transaction"]

    async def get_account_details(self, access_token: str, consent_id: str, user_id: str, account_id: str) -> dict:
        """
        Получает детальную информацию о конкретном счете из SBank.
        """
        response = await self.client.get(
            f"{self.api_url}/accounts/{account_id}",
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-Requesting-Bank": settings.CLIENT_ID,
                "X-Consent-Id": consent_id
            },
            params={"client_id": user_id}
        )
        response.raise_for_status()
        response_data = response.json()
        if "data" not in response_data or "account" not in response_data["data"]:
            raise ValueError(f"Неожиданная структура ответа от SBank при получении деталей счета: {response_data}")
        return response_data["data"]["account"]
