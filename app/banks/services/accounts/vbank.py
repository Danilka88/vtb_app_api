from app.banks.services.accounts.base import BaseAccountsService
from app.core.config import settings


class VBankAccountsService(BaseAccountsService):
    """
    Сервис для работы со счетами в VBank.
    Реализует специфическую логику взаимодействия с API VBank для получения
    информации о счетах, балансах и транзакциях.
    """

    def __init__(self, client): # client будет экземпляром VBankClient
        self._client = client

    async def get_accounts(self, access_token: str, consent_id: str, user_id: str) -> list[dict]:
        """
        Получает список счетов пользователя из VBank.
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
        # Проверяем ожидаемую структуру ответа от API VBank
        if "data" not in response_data or "account" not in response_data["data"]:
            raise ValueError(f"Неожиданная структура ответа от VBank при получении счетов: {response_data}")
        return response_data["data"]["account"]

    async def get_account_balances(self, access_token: str, consent_id: str, user_id: str, account_id: str) -> dict:
        """
        Получает балансы для конкретного счета из VBank.
        Требует `access_token` и `consent_id` с разрешением `ReadBalances`.
        """
        response = await self._client._async_client.post(
            f"{self._client.api_url}/accounts/{account_id}/balances",
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-Requesting-Bank": settings.CLIENT_ID,
                "X-Consent-Id": consent_id,
                "Content-Type": "application/json"
            },
            json={"user_id": user_id}
        )
        response.raise_for_status()
        response_data = response.json()
        # Проверяем ожидаемую структуру ответа от API VBank
        if "data" not in response_data or "balance" not in response_data["data"]:
            raise ValueError(f"Неожиданная структура ответа от VBank при получении балансов: {response_data}")
        return response_data["data"]["balance"]

    async def get_account_transactions(self, access_token: str, consent_id: str, user_id: str, account_id: str) -> list[dict]:
        """
        Получает историю транзакций для конкретного счета из VBank.
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
        # Проверяем ожидаемую структуру ответа от API VBank
        if "data" not in response_data or "transaction" not in response_data["data"]:
            raise ValueError(f"Неожиданная структура ответа от VBank при получении транзакций: {response_data}")
        return response_data["data"]["transaction"]

    async def create_account(self, access_token: str, account_data: dict) -> dict:
        """
        Создает новый счет для пользователя в VBank.
        Требует `access_token`.
        """
        print(f"DEBUG: Отправка запроса на создание счета в VBank. account_data: {account_data}")
        response = await self._client._async_client.post(
            f"{self._client.api_url}/accounts",
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-Requesting-Bank": settings.CLIENT_ID,
                "Content-Type": "application/json"
            },
            json=account_data # Передаем только account_type и initial_balance
        )
        response.raise_for_status()
        return response.json()

    async def get_account_details(self, access_token: str, consent_id: str, user_id: str, account_id: str) -> dict:
        """
        Получает детальную информацию о конкретном счете из VBank.
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
        response.raise_for_status()
        response_data = response.json()
        if "data" not in response_data or "account" not in response_data["data"]:
            raise ValueError(f"Неожиданная структура ответа от VBank при получении деталей счета: {response_data}")
        return response_data["data"]["account"]

    async def update_account_status(self, access_token: str, user_id: str, account_id: str, status: str) -> dict:
        """
        Изменяет статус счета пользователя в VBank.
        Требует `access_token`.
        """
        response = await self._client._async_client.put(
            f"{self._client.api_url}/accounts/{account_id}/status",
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-Requesting-Bank": settings.CLIENT_ID,
                "Content-Type": "application/json"
            },
            json={"status": status, "client_id": user_id}
        )
        response.raise_for_status()
        return response.json()

    async def close_account(self, access_token: str, user_id: str, account_id: str) -> dict:
        """
        Закрывает счет пользователя в VBank.
        Требует `access_token`.
        """
        response = await self._client._async_client.put(
            f"{self._client.api_url}/accounts/{account_id}/close",
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-Requesting-Bank": settings.CLIENT_ID,
                "Content-Type": "application/json"
            },
            json={"client_id": user_id}
        )
        response.raise_for_status()
        return response.json()
