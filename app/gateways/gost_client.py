import asyncio
import httpx

from app.banks.base_client import BaseBankClient
from app.security.jwt_utils import create_signed_ciba_jwt


class GostClient(BaseBankClient):
    async def initiate_ciba_authentication(self, login_hint: str, binding_message: str) -> dict:
        signed_jwt = create_signed_ciba_jwt(login_hint, binding_message, self.api_url)
        response = await self.client.post(
            f"{self.api_url}/bc-authorize",
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data={
                "client_id": self.client_id,
                "request": signed_jwt
            }
        )
        response.raise_for_status()
        return response.json()

    async def poll_for_tokens(self, auth_req_id: str) -> dict:
        while True:
            response = await self.client.post(
                f"{self.api_url}/token",
                data={
                    "grant_type": "urn:openid:params:grant-type:ciba",
                    "auth_req_id": auth_req_id,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret  # For client authentication
                }
            )
            try:
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 400:
                    error_data = e.response.json()
                    if error_data.get("error") == "authorization_pending":
                        await asyncio.sleep(5)  # Poll every 5 seconds
                        continue
                    elif error_data.get("error") == "slow_down":
                        await asyncio.sleep(error_data.get("interval", 5)) # Use interval if provided
                        continue
                raise  # Re-raise other HTTP errors
