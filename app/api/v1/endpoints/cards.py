from fastapi import APIRouter, Depends, Header, HTTPException
from typing import List, Optional

from app.schemas.card import Card
from app.utils.bank_clients import get_bank_client
from app.banks.base_client import BaseBankClient
from app.auth_manager.dependencies import get_user_bank_token, get_current_user_id

router = APIRouter()

@router.get("/{bank_name}/cards", response_model=List[Card], tags=["Cards"])
async def get_cards(
    bank_name: str,
    consent_id: str = Header(..., description="Consent ID for accessing card data"),
    user_id: str = Depends(get_current_user_id),
    bank_client: BaseBankClient = Depends(get_bank_client),
    token: str = Depends(get_user_bank_token),
):
    """
    Получение списка карт клиента из указанного банка.
    """
    try:
        cards_data = await bank_client.cards.get_cards(
            access_token=token,
            user_id=user_id,
            consent_id=consent_id
        )
        return [Card(**card) for card in cards_data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{bank_name}/cards/{card_id}", response_model=Card, tags=["Cards"])
async def get_card_details(
    bank_name: str,
    card_id: str,
    consent_id: str = Header(..., description="Consent ID for accessing card data"),
    user_id: str = Depends(get_current_user_id),
    bank_client: BaseBankClient = Depends(get_bank_client),
    token: str = Depends(get_user_bank_token),
):
    """
    Получение детальной информации по конкретной карте.
    """
    try:
        card_data = await bank_client.cards.get_card_details(
            access_token=token,
            user_id=user_id,
            consent_id=consent_id,
            card_id=card_id
        )
        return Card(**card_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
