import httpx
from datetime import datetime, timedelta

from app.banks.base_client import BaseBankClient
from app.core.config import settings


class ABankClient(BaseBankClient):
    async def get_bank_token(self) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/auth/bank-token",
                params={"client_id": self.client_id, "client_secret": self.client_secret}
            )
            response.raise_for_status()
            return response.json()

    async def create_consent(self, access_token: str, permissions: list[str], user_id: str) -> str:
        now = datetime.utcnow()
        expiration_date = (now + timedelta(days=365)).isoformat(timespec='seconds') + 'Z'
        transaction_from_date = (now - timedelta(days=365)).isoformat(timespec='seconds') + 'Z'
        transaction_to_date = now.isoformat(timespec='seconds') + 'Z'

        async with httpx.AsyncClient() as client:
            response = await client.post(
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

    async def get_accounts(self, access_token: str, consent_id: str, user_id: str) -> list[dict]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/accounts",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "X-Requesting-Bank": settings.CLIENT_ID,
                    "X-Consent-Id": consent_id
                },
                params={
                    "client_id": user_id
                }
            )
            response.raise_for_status()
            response_data = response.json()
            if "data" not in response_data or "account" not in response_data["data"]:
                raise ValueError(f"Expected 'data.account' in response, but got: {response_data}")
            return response_data["data"]["account"]

    async def get_account_balances(self, access_token: str, consent_id: str, user_id: str, account_id: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/accounts/{account_id}/balances",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "X-Requesting-Bank": settings.CLIENT_ID,
                    "X-Consent-Id": consent_id
                },
                params={
                    "client_id": user_id
                }
            )
            response.raise_for_status()
            response_data = response.json()
            if "data" not in response_data or "balance" not in response_data["data"]:
                raise ValueError(f"Expected 'data.balance' in response, but got: {response_data}")
            return response_data["data"]["balance"]

    async def get_account_transactions(self, access_token: str, consent_id: str, user_id: str, account_id: str) -> list[dict]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/accounts/{account_id}/transactions",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "X-Requesting-Bank": settings.CLIENT_ID,
                    "X-Consent-Id": consent_id
                },
                params={
                    "client_id": user_id
                }
            )
            response.raise_for_status()
            response_data = response.json()
            if "data" not in response_data or "transaction" not in response_data["data"]:
                raise ValueError(f"Expected 'data.transaction' in response, but got: {response_data}")
            return response_data["data"]["transaction"]
