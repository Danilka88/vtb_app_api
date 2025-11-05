from abc import ABC, abstractmethod

from app.banks.services.base_service import BaseService


class BaseAccountsService(BaseService, ABC):
    """
    Абстрактный базовый класс для сервисов, работающих со счетами в банках.
    Определяет общий интерфейс для получения информации о счетах, балансах и транзакциях,
    который должен быть реализован для каждого конкретного банка.
    """

    @abstractmethod
    async def get_accounts(self, access_token: str, consent_id: str, user_id: str) -> list[dict]:
        """
        Получает список всех счетов пользователя.
        """
        pass

    @abstractmethod
    async def get_account_balances(self, access_token: str, consent_id: str, user_id: str, account_id: str) -> dict:
        """
        Получает баланс для конкретного счета.
        """
        pass

    @abstractmethod
    async def get_account_transactions(self, access_token: str, consent_id: str, user_id: str, account_id: str) -> list[dict]:
        """
        Получает историю транзакций для конкретного счета.
        """
        pass

    @abstractmethod
    async def get_account_details(self, access_token: str, consent_id: str, user_id: str, account_id: str) -> dict:
        """
        Получает детальную информацию о конкретном счете.
        """
        pass
