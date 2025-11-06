from pydantic import BaseModel, Field
from typing import List, Optional, Any

class MultiBankAccountsRequest(BaseModel):
    """
    Модель запроса для получения счетов из нескольких банков.
    """
    bank_names: List[str] = Field(..., description="Список названий банков (например, ['vbank', 'abank'])")
    user_id: str = Field(..., description="Идентификатор пользователя, для которого запрашиваются счета")

class BankOperationResponse(BaseModel):
    """
    Унифицированная модель ответа для операций с банками.
    """
    bank_name: str = Field(..., description="Название банка")
    status: str = Field(..., description="Статус операции (например, 'success', 'failed', 'pending')")
    message: Optional[str] = Field(None, description="Сообщение об операции")
    data: Optional[Any] = Field(None, description="Данные, возвращенные банком")
    error: Optional[str] = Field(None, description="Сообщение об ошибке, если операция не удалась")

class MultiBankConsentRequest(BaseModel):
    """
    Модель запроса для создания согласия через MCP.
    """
    bank_name: str = Field(..., description="Название банка")
    permissions: List[str] = Field(..., description="Список запрашиваемых разрешений")
    user_id: str = Field(..., description="Идентификатор пользователя")
    debtor_account: Optional[str] = Field(None, description="Идентификатор счета дебитора (для платежных согласий)")
    amount: Optional[str] = Field(None, description="Сумма платежа (для платежных согласий)")
    currency: Optional[str] = Field("RUB", description="Валюта платежа (для платежных согласий)")
