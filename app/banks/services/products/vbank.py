
from typing import List

from app.banks.services.products.base import BaseProductsService
from app.schemas.product import Product, ProductAgreement, ProductAgreementCreateRequest
from app.core.config import settings

class VBankProductsService(BaseProductsService):
    """
    Сервис для работы с продуктами в VBank.
    """

    async def get_products(self, access_token: str) -> List[Product]:
        response = await self.client.get(
            f"{self.api_url}/products",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        response.raise_for_status()
        products_data = response.json()
        # Проверяем, что 'data' и 'product' существуют и являются списками
        if isinstance(products_data, dict) and "data" in products_data and \
           isinstance(products_data["data"], dict) and "product" in products_data["data"] and \
           isinstance(products_data["data"]["product"], list):
            products_list = products_data["data"]["product"]
        elif isinstance(products_data, list):
            products_list = products_data
        else:
            products_list = []

        return [Product(**p) for p in products_list if isinstance(p, dict)]

    async def get_product_details(self, access_token: str, product_id: str) -> Product:
        response = await self.client.get(
            f"{self.api_url}/products/{product_id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        response.raise_for_status()
        return Product(**response.json().get("data", {}))

    async def get_product_agreements(self, access_token: str, consent_id: str, user_id: str) -> List[ProductAgreement]:
        response = await self.client.get(
            f"{self.api_url}/product-agreements",
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-Consent-Id": consent_id
            },
            params={"client_id": user_id}
        )
        response.raise_for_status()
        return [ProductAgreement(**pa) for pa in response.json().get("data", [])]

    async def create_product_agreement(self, access_token: str, consent_id: str, user_id: str, request: ProductAgreementCreateRequest) -> ProductAgreement:
        response = await self.client.post(
            f"{self.api_url}/product-agreements",
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-Consent-Id": consent_id,
                "Content-Type": "application/json"
            },
            json=request.model_dump(by_alias=True),
            params={"client_id": user_id}
        )
        response.raise_for_status()
        return ProductAgreement(**response.json().get("data", {}))

    async def get_product_agreement_details(self, access_token: str, consent_id: str, user_id: str, agreement_id: str) -> ProductAgreement:
        response = await self.client.get(
            f"{self.api_url}/product-agreements/{agreement_id}",
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-Consent-Id": consent_id
            },
            params={"client_id": user_id}
        )
        response.raise_for_status()
        return ProductAgreement(**response.json().get("data", {}))

    async def close_product_agreement(self, access_token: str, consent_id: str, user_id: str, agreement_id: str) -> dict:
        response = await self.client.delete(
            f"{self.api_url}/product-agreements/{agreement_id}",
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-Consent-Id": consent_id
            },
            params={"client_id": user_id}
        )
        response.raise_for_status()
        return {"status": "success", "message": f"Agreement {agreement_id} closed."}
