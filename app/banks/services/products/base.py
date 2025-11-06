
from abc import ABC, abstractmethod
from typing import List

from app.banks.services.base_service import BaseService
from app.schemas.product import Product, ProductAgreement, ProductAgreementCreateRequest

class BaseProductsService(BaseService, ABC):
    """
    Абстрактный базовый класс для сервисов, работающих с банковскими продуктами.
    Определяет общий интерфейс для получения каталога продуктов и управления договорами.
    """

    @abstractmethod
    async def get_products(self, access_token: str) -> List[Product]:
        """
        Получает каталог банковских продуктов.
        """
        pass

    @abstractmethod
    async def get_product_details(self, access_token: str, product_id: str) -> Product:
        """
        Получает детальную информацию о конкретном продукте.
        """
        pass

    @abstractmethod
    async def get_product_agreements(self, access_token: str, consent_id: str, user_id: str) -> List[ProductAgreement]:
        """
        Получает список договоров клиента по продуктам.
        """
        pass

    @abstractmethod
    async def create_product_agreement(self, access_token: str, consent_id: str, user_id: str, request: ProductAgreementCreateRequest) -> ProductAgreement:
        """
        Создает новый договор по продукту (например, открывает вклад).
        """
        pass

    @abstractmethod
    async def get_product_agreement_details(self, access_token: str, consent_id: str, user_id: str, agreement_id: str) -> ProductAgreement:
        """
        Получает детали конкретного договора.
        """
        pass

    @abstractmethod
    async def close_product_agreement(self, access_token: str, consent_id: str, user_id: str, agreement_id: str) -> dict:
        """
        Закрывает (расторгает) договор по продукту.
        """
        pass
