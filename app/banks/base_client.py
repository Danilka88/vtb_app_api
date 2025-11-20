from abc import ABC, abstractmethod
import httpx

from app.core.config import settings
from app.auth_manager.schemas import TokenResponse

from app.banks.services.accounts.base import BaseAccountsService
from app.banks.services.payments.base import BasePaymentsService
from app.banks.services.products.base import BaseProductsService
from app.banks.services.cards.base import BaseCardsService


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
        self._async_client = self._create_http_client()

    def _create_http_client(self) -> httpx.AsyncClient:
        """
        Фабричный метод для создания HTTP-клиента.
        Позволяет в будущем легко подменять реализацию для поддержки mTLS, GOST и т.д.
        """
        if settings.CLIENT_CERT_PATH and settings.CLIENT_KEY_PATH:
            print(f"DEBUG: Инициализация httpx.AsyncClient с mTLS. Cert: {settings.CLIENT_CERT_PATH}, Key: {settings.CLIENT_KEY_PATH}")
            cert = (settings.CLIENT_CERT_PATH, settings.CLIENT_KEY_PATH)
            return httpx.AsyncClient(cert=cert)
        else:
            print("DEBUG: Инициализация httpx.AsyncClient без mTLS.")
            return httpx.AsyncClient()

    @abstractmethod
    async def get_bank_token(self) -> TokenResponse:
        """
        Абстрактный метод для получения токена доступа от банка.
        Каждый клиент должен реализовать свою логику запроса к /auth/bank-token.
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

    @abstractmethod
    async def get_consent(self, access_token: str, consent_id: str, user_id: str) -> dict:
        """
        Абстрактный метод для получения информации о согласии по его ID.
        """
        pass

    @abstractmethod
    async def revoke_consent(self, access_token: str, consent_id: str, user_id: str) -> dict:
        """
        Абстрактный метод для отзыва согласия по его ID.
        """
        pass

    @abstractmethod
    async def create_product_agreement_consent(self, access_token: str, permissions: list[str], user_id: str) -> str:
        """
        Абстрактный метод для создания согласия на управление договорами.
        """
        pass

    @abstractmethod
    async def get_product_agreement_consent(self, access_token: str, consent_id: str, user_id: str) -> dict:
        """
        Абстрактный метод для получения информации о согласии на управление договорами.
        """
        pass

    @abstractmethod
    async def revoke_product_agreement_consent(self, access_token: str, consent_id: str, user_id: str) -> dict:
        """
        Абстрактный метод для отзыва согласия на управление договорами.
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

    @property
    @abstractmethod
    def products(self) -> BaseProductsService:
        """
        Абстрактное свойство, возвращающее сервис для работы с продуктами банка.
        Должно быть реализовано в классах-наследниках.
        """
        pass

    @property
    @abstractmethod
    def cards(self) -> BaseCardsService:
        """
        Абстрактное свойство, возвращающее сервис для работы с картами банка.
        """
        pass

    @abstractmethod
    async def get_cards(self, access_token: str, user_id: str, consent_id: str) -> list[dict]:
        """
        Абстрактный метод для получения списка карт.
        """
        pass

    @abstractmethod
    async def get_card_details(self, access_token: str, user_id: str, consent_id: str, card_id: str) -> dict:
        """
        Абстрактный метод для получения деталей карты.
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
