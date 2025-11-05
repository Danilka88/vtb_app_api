from pydantic import BaseModel, Field
from typing import Optional


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
