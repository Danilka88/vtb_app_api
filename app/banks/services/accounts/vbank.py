import httpx

from app.banks.services.accounts.base import BaseAccountsService
from app.core.config import settings


class VBankAccountsService(BaseAccountsService):
    """
    Сервис для работы со счетами в VBank.
    Реализует специфическую логику взаимодействия с API VBank для получения
    информации о счетах, балансах и транзакциях.
    """

    async def get_accounts(self, access_token: str, consent_id: str, user_id: str) -> list[dict]:
        """
        Получает список счетов пользователя из VBank.
        Требует `access_token` и `consent_id` с разрешением `ReadAccountsDetail`.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
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
            # Проверяем ожидаемую структуру ответа от API VBank
            if "data" not in response_data or "account" not in response_data["data"]:
                raise ValueError(f"Неожиданная структура ответа от VBank при получении счетов: {response_data}")
            return response_data["data"]["account"]

    async def get_account_balances(self, access_token: str, consent_id: str, user_id: str, account_id: str) -> dict:
        """
        Получает балансы для конкретного счета из VBank.
        Требует `access_token` и `consent_id` с разрешением `ReadBalances`.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
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
            # Проверяем ожидаемую структуру ответа от API VBank
            if "data" not in response_data or "balance" not in response_data["data"]:
                raise ValueError(f"Неожиданная структура ответа от VBank при получении балансов: {response_data}")
            return response_data["data"]["balance"]

    async def get_account_transactions(self, access_token: str, consent_id: str, user_id: str, account_id: str) -> list[dict]:
        """
        Получает историю транзакций для конкретного счета из VBank.
        Требует `access_token` и `consent_id` с разрешением `ReadTransactionsDetail`.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
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
            # Проверяем ожидаемую структуру ответа от API VBank
            if "data" not in response_data or "transaction" not in response_data["data"]:
                raise ValueError(f"Неожиданная структура ответа от VBank при получении транзакций: {response_data}")
            return response_data["data"]["transaction"]

    async def get_account_details(self, access_token: str, consent_id: str, user_id: str, account_id: str) -> dict:
        """
        Получает детальную информацию о конкретном счете из VBank.
        На данный момент не реализовано.
        """
        raise NotImplementedError("Метод get_account_details не реализован для VBank")
