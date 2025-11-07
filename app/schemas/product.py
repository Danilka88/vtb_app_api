
from pydantic import BaseModel, Field
from typing import Optional, List

class FinancialGoal(BaseModel):
    """
    Модель данных для финансовой цели пользователя.
    """
    id: str = Field(..., description="Уникальный идентификатор цели")
    name: str = Field(..., description="Название цели")
    current_amount: float = Field(..., description="Текущая накопленная сумма")
    target_amount: float = Field(..., description="Целевая сумма")


class Product(BaseModel):
    """
    Схема для представления банковского продукта в каталоге.
    """
    product_id: str = Field(..., alias="productId")
    name: str = Field(..., alias="productName")
    category: str = Field(..., alias="productType") # Например, "Deposits", "Loans", "Cards"
    description: Optional[str] = None
    interest_rate: Optional[float] = Field(None, alias="interestRate")

class ProductAgreement(BaseModel):
    """
    Схема для представления договора по банковскому продукту.
    """
    agreement_id: str = Field(..., alias="agreementId")
    product_id: str = Field(..., alias="productId")
    user_id: str = Field(..., alias="userId")
    status: str # Например, "Active", "Closed"
    open_date: str = Field(..., alias="openDate")

class ProductAgreementConsentRequest(BaseModel):
    """
    Схема для запроса на создание согласия на управление договорами.
    """
    bank_name: str
    user_id: str
    permissions: List[str] = ["ReadProductAgreements", "CreateProductAgreements", "DeleteProductAgreements"]

class ProductAgreementCreateRequest(BaseModel):
    """
    Схема для запроса на открытие нового продукта (создание договора).
    """
    product_id: str = Field(..., alias="productId")
    user_id: str = Field(..., alias="userId")
    initial_amount: Optional[float] = Field(None, alias="initialAmount") # Например, для вклада
