from .base import BaseCardsService

class SBankCardsService(BaseCardsService):
    """
    Сервис для работы с картами в SBank.
    """
    async def get_cards(self, access_token: str, user_id: str, consent_id: str) -> list[dict]:
        """
        Получение списка карт пользователя из SBank.
        """
        return await self.client.get_cards(access_token, user_id, consent_id)

    async def get_card_details(self, access_token: str, user_id: str, consent_id: str, card_id: str) -> dict:
        """
        Получение детальной информации по карте из SBank.
        """
        return await self.client.get_card_details(access_token, user_id, consent_id, card_id)
