from .base import BaseCardsService

class VBankCardsService(BaseCardsService):
    """
    Сервис для работы с картами в VBank.
    """
    async def get_cards(self, access_token: str, user_id: str, consent_id: str) -> list[dict]:
        """
        Получение списка карт пользователя из VBank.
        """
        return await self.client.get_cards(access_token, user_id, consent_id)

    async def get_card_details(self, access_token: str, user_id: str, consent_id: str, card_id: str) -> dict:
        """
        Получение детальной информации по карте из VBank.
        """
        return await self.client.get_card_details(access_token, user_id, consent_id, card_id)
