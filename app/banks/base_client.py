from abc import ABC, abstractmethod


class BaseBankClient(ABC):
    def __init__(self, client_id: str, client_secret: str, api_url: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.api_url = api_url

    @abstractmethod
    async def get_bank_token(self) -> dict:
        pass

    @abstractmethod
    async def create_consent(self, access_token: str, permissions: list[str], user_id: str) -> str:
        pass

    @abstractmethod
    async def get_accounts(self, access_token: str, consent_id: str, user_id: str) -> list[dict]:
        pass

    @abstractmethod
    async def get_account_balances(self, access_token: str, consent_id: str, user_id: str, account_id: str) -> dict:
        pass

    @abstractmethod
    async def get_account_transactions(self, access_token: str, consent_id: str, user_id: str, account_id: str) -> list[dict]:
        pass

    @abstractmethod
    async def get_account_details(self, access_token: str, consent_id: str, user_id: str, account_id: str) -> dict:
        pass
