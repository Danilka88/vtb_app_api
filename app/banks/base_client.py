from abc import ABC, abstractmethod
import httpx

from app.banks.services.accounts.base import BaseAccountsService
from app.banks.services.payments.base import BasePaymentsService


class BaseBankClient(ABC):
    """
    Абстрактный базовый класс для всех клиентов банков.
    Предоставляет общую структуру для взаимодействия с API различных банков,
    включая инициализацию HTTP-клиента и базовые методы для получения токенов и создания согласий.
    """
    def __init__(self, client_id: str, client_secret: str, api_url: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.api_url = api_url
        # Инициализируем асинхронный HTTP-клиент httpx.
        # В будущем здесь будет добавлена конфигурация mTLS.
        self._async_client = httpx.AsyncClient()

    @abstractmethod
    async def get_bank_token(self) -> dict:
        """
        Абстрактный метод для получения токена доступа банка.
        Должен быть реализован в классах-наследниках для каждого конкретного банка.
        Возвращает словарь с данными токена (access_token, expires_in).
        """
        pass

    @abstractmethod
    async def create_consent(self, access_token: str, permissions: list[str], user_id: str) -> str:
        """
        Абстрактный метод для создания согласия на доступ к данным или на выполнение платежа.
        Должен быть реализован в классах-наследниках.
        Принимает токен доступа, список разрешений и ID пользователя.
        Возвращает идентификатор созданного согласия (consent_id).
        """
        pass

    @property
    @abstractmethod
    def accounts(self) -> BaseAccountsService:
        """
        Абстрактное свойство, возвращающее сервис для работы со счетами банка.
        Должно быть реализовано в классах-наследниках.
        """
        pass

    @property
    @abstractmethod
    def payments(self) -> BasePaymentsService:
        """
        Абстрактное свойство, возвращающее сервис для работы с платежами банка.
        Должно быть реализовано в классах-наследниках.
        """
        pass

    async def __aenter__(self):
        """
        Вход в асинхронный контекстный менеджер.
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Выход из асинхронного контекстного менеджера.
        Закрывает асинхронный HTTP-клиент.
        """
        await self._async_client.aclose()
