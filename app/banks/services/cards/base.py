from abc import ABC, abstractmethod

class BaseCardsService(ABC):
    """
    Абстрактный базовый класс для сервиса по работе с картами.
    Определяет общие методы, которые должен реализовывать каждый банковский клиент.
    """
    def __init__(self, client):
        self.client = client
        self.api_url = client.api_url

    @abstractmethod
    async def get_cards(self, access_token: str, user_id: str, consent_id: str) -> list[dict]:
        """
        Получение списка карт пользователя.
        """
        pass

    @abstractmethod
    async def get_card_details(self, access_token: str, user_id: str, consent_id: str, card_id: str) -> dict:
        """
        Получение детальной информации по карте.
        """
        pass
