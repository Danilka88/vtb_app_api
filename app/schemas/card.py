from pydantic import BaseModel, Field
from typing import Optional, List

class Card(BaseModel):
    card_id: str = Field(..., description="Уникальный идентификатор карты")
    account_id: str = Field(..., description="Идентификатор счета, к которому привязана карта")
    status: str = Field(..., description="Статус карты (например, Active, Blocked)")
    card_type: str = Field(..., description="Тип карты (например, Debit, Credit)")
    pan_masked: str = Field(..., description="Маскированный номер карты")
    expiry_date: str = Field(..., description="Срок действия карты")
    holder_name: Optional[str] = Field(None, description="Имя держателя карты")

class CardCollection(BaseModel):
    cards: List[Card]
