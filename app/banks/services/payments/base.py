from abc import ABC, abstractmethod
from pydantic import BaseModel

from app.banks.services.base_service import BaseService

from app.schemas.payment import PaymentInitiationRequest, VRPPaymentRequest, VRPConsentRequest

class BasePaymentsService(BaseService, ABC):
    """
    Абстрактный базовый класс для сервисов, работающих с платежами в банках.
    Определяет общий интерфейс для создания платежей, получения их статуса,
    а также для работы с согласиями и платежами VRP (Variable Recurring Payments).
    """

    @abstractmethod
    async def create_payment(self, access_token: str, payment_request: PaymentInitiationRequest, consent_id: str) -> dict:
        """
        Абстрактный метод для создания разового платежа.
        """
        pass

    @abstractmethod
    async def get_payment_status(self, access_token: str, payment_id: str, client_id: str) -> dict:
        """
        Абстрактный метод для получения статуса платежа по его ID.
        """
        pass

    @abstractmethod
    async def create_vrp_consent(self, access_token: str, user_id: str, vrp_data: VRPConsentRequest) -> dict:
        """
        Абстрактный метод для создания согласия на периодические платежи (VRP).
        """
        pass

    @abstractmethod
    async def get_vrp_consent(self, access_token: str, user_id: str, consent_id: str) -> dict:
        """
        Абстрактный метод для получения информации о VRP согласии.
        """
        pass

    @abstractmethod
    async def create_vrp_payment(self, access_token: str, consent_id: str, user_id: str, payment_data: VRPPaymentRequest) -> VRPStatus:
        """
        Абстрактный метод для инициирования платежа в рамках VRP согласия.
        """
        pass
