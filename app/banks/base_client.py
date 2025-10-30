from abc import ABC, abstractmethod


class BaseBankClient(ABC):
    def __init__(self, client_id: str, client_secret: str, api_url: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.api_url = api_url

    @abstractmethod
    async def get_bank_token(self) -> dict:
        pass
