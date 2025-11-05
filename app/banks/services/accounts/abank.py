import httpx
import json

from app.banks.services.accounts.base import BaseAccountsService
from app.core.config import settings


class ABankAccountsService(BaseAccountsService):
    """
    Сервис для работы со счетами в ABank.
    Реализует специфическую логику взаимодействия с API ABank для получения
    информации о счетах, балансах и транзакциях.
    """

    async def get_accounts(self, access_token: str, consent_id: str, user_id: str) -> list[dict]:
        """
        Получает список счетов пользователя из ABank.
        Требует `access_token` и `consent_id` с разрешением `ReadAccountsDetail`.
        """
        response = await self._client._async_client.get(
            f"{self._client.api_url}/accounts",
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-Requesting-Bank": settings.CLIENT_ID,
                "X-Consent-Id": consent_id
            },
            params={"client_id": user_id}
        )
        response.raise_for_status()
        response_data = response.json()
        # Проверяем ожидаемую структуру ответа от API ABank
        if "data" not in response_data or "account" not in response_data["data"]:
            raise ValueError(f"Неожиданная структура ответа от ABank при получении счетов: {response_data}")
        return response_data["data"]["account"]

    async def get_account_balances(self, access_token: str, consent_id: str, user_id: str, account_id: str) -> dict:
        """
        Получает балансы для конкретного счета из ABank.
        Требует `access_token` и `consent_id` с разрешением `ReadBalances`.
        """
        response = await self._client._async_client.get(
            f"{self._client.api_url}/accounts/{account_id}/balances",
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-Requesting-Bank": settings.CLIENT_ID,
                "X-Consent-Id": consent_id
            },
            params={"client_id": user_id}
        )
        response.raise_for_status()
        response_data = response.json()
        # Проверяем ожидаемую структуру ответа от API ABank
        if "data" not in response_data or "balance" not in response_data["data"]:
            raise ValueError(f"Неожиданная структура ответа от ABank при получении балансов: {response_data}")
        return response_data["data"]["balance"]

    async def get_account_transactions(self, access_token: str, consent_id: str, user_id: str, account_id: str) -> list[dict]:
        """
        Получает историю транзакций для конкретного счета из ABank.
        Требует `access_token` и `consent_id` с разрешением `ReadTransactionsDetail`.
        """
        response = await self._client._async_client.get(
            f"{self._client.api_url}/accounts/{account_id}/transactions",
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-Requesting-Bank": settings.CLIENT_ID,
                "X-Consent-Id": consent_id
            },
            params={"client_id": user_id}
        )
        response.raise_for_status()
        response_data = response.json()
        # Проверяем ожидаемую структуру ответа от API ABank
        if "data" not in response_data or "transaction" not in response_data["data"]:
            raise ValueError(f"Неожиданная структура ответа от ABank при получении транзакций: {response_data}")
        return response_data["data"]["transaction"]

    async def get_account_details(self, access_token: str, consent_id: str, user_id: str, account_id: str) -> dict:
        """
        Получает детальную информацию о конкретном счете из ABank.
        Требует `access_token` и `consent_id` с разрешением `ReadAccountsDetail`.
        """
        response = await self._client._async_client.get(
            f"{self._client.api_url}/accounts/{account_id}",
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-Requesting-Bank": settings.CLIENT_ID,
                "X-Consent-Id": consent_id
            },
            params={"client_id": user_id}
        )
        # Проверяем статус ответа до парсинга JSON
        if response.status_code >= 400:
            response.raise_for_status() # Это вызовет httpx.HTTPStatusError
        
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            raise ValueError(f"Не удалось распарсить JSON ответ от ABank API: {response.text}")

        if "data" not in response_data or "account" not in response_data["data"]:
            raise ValueError(f"Неожиданная структура ответа от ABank при получении деталей счета: {response_data}")
        
        if isinstance(response_data["data"]["account"], list) and len(response_data["data"]["account"]) > 0:
            return response_data["data"]["account"][0]
        elif isinstance(response_data["data"]["account"], dict):
            return response_data["data"]["account"]
        else:
            raise ValueError(f"Неожиданный формат данных счета в ответе от ABank: {response_data['data']['account']}")
