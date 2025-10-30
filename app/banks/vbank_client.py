import httpx

from app.banks.base_client import BaseBankClient


class VBankClient(BaseBankClient):
    async def get_bank_token(self) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/auth/bank-token",
                params={"client_id": self.client_id, "client_secret": self.client_secret}
            )
            response.raise_for_status()  # Raise an exception for bad status codes
            return response.json()
