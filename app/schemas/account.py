from pydantic import BaseModel, Field
from typing import Optional


class Account(BaseModel):
    """
    Модель данных для банковского счета.
    """
    account_id: str = Field(..., description="Уникальный идентификатор счета")
    bank_name: str = Field(..., description="Название банка")
    account_name: str = Field(..., description="Название счета (например, 'Текущий', 'Накопительный')")
    account_type: str = Field(..., description="Тип счета (например, 'debit', 'credit', 'savings')")
    balance: float = Field(..., description="Текущий баланс счета")
    currency: str = Field(..., description="Валюта счета (например, 'RUB', 'USD')")
    status: str = Field(..., description="Статус счета (например, 'active', 'inactive')")
    last_four: Optional[str] = Field(None, description="Последние четыре цифры номера счета")
    brand_color: Optional[str] = Field(None, description="Цвет бренда банка для UI")


class AccountCreateRequest(BaseModel):
    """
    Модель запроса для создания нового счета.
    """
    account_type: str = Field(..., description="Тип счета (например, checking, savings)")
    initial_balance: float = Field(0.0, description="Начальный баланс счета")


class AccountDetailsRequest(BaseModel):
    """
    Модель запроса для получения деталей счета.
    """
    bank_name: str
    consent_id: str
    user_id: str


class AccountStatusUpdateRequest(BaseModel):
    """
    Модель запроса для изменения статуса счета.
    """
    bank_name: str
    user_id: str
    status: str = Field(..., description="Новый статус счета (например, Enabled, Disabled, Deleted)")


class AccountCloseRequest(BaseModel):
    """
    Модель запроса для закрытия счета.
    """
    bank_name: str
    user_id: str
