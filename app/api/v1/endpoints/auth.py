from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import httpx

from app.core.config import settings
from app.db import crud
from app.db.database import SessionLocal
from app.banks.vbank_client import VBankClient
from app.banks.abank_client import ABankClient
from app.banks.sbank_client import SBankClient

router = APIRouter()


class ConsentRequest(BaseModel):
    bank_name: str
    permissions: list[str] = [
        "ReadAccountsDetail",
        "ReadBalances",
        "ReadTransactionsCredits",
        "ReadTransactionsDebits",
        "ReadTransactionsDetail",
        "ReadBeneficiariesDetail",
        "ReadDirectDebits",
        "ReadStandingOrders",
        "ReadProducts",
        "ReadOffers",
        "ReadStatements"
    ]
    user_id: str # Идентификатор пользователя, например, team042-1


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/init-bank-tokens")
async def init_bank_tokens(db: Session = Depends(get_db)):
    """
    Initializes and saves bank tokens for all supported banks using the simple bank-token flow.
    """
    bank_clients = {
        "vbank": VBankClient(client_id=settings.CLIENT_ID, client_secret=settings.CLIENT_SECRET, api_url=settings.VBANK_API_URL),
        "abank": ABankClient(client_id=settings.CLIENT_ID, client_secret=settings.CLIENT_SECRET, api_url=settings.ABANK_API_URL),
        "sbank": SBankClient(client_id=settings.CLIENT_ID, client_secret=settings.CLIENT_SECRET, api_url=settings.SBANK_API_URL),
    }

    for bank_name, bank_client in bank_clients.items():
        try:
            token_data = await bank_client.get_bank_token()
            crud.save_token(
                db=db,
                bank_name=bank_name,
                token=token_data["access_token"],
                expires_in=token_data["expires_in"]
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get token for {bank_name}: {e}")

    return {"message": "Bank tokens initialized successfully."}


@router.post("/create-consent")
async def create_consent(request: ConsentRequest, db: Session = Depends(get_db)):
    """
    Creates a consent for a given bank with specified permissions.
    """
    bank_name = request.bank_name.lower()
    permissions = request.permissions
    user_id = request.user_id

    if bank_name == "vbank":
        bank_client = VBankClient(client_id=settings.CLIENT_ID, client_secret=settings.CLIENT_SECRET, api_url=settings.VBANK_API_URL)
    elif bank_name == "abank":
        bank_client = ABankClient(client_id=settings.CLIENT_ID, client_secret=settings.CLIENT_SECRET, api_url=settings.ABANK_API_URL)
    elif bank_name == "sbank":
        bank_client = SBankClient(client_id=settings.CLIENT_ID, client_secret=settings.CLIENT_SECRET, api_url=settings.SBANK_API_URL)
    else:
        raise HTTPException(status_code=400, detail="Unsupported bank.")

    access_token = crud.get_decrypted_token(db, bank_name)
    if not access_token:
        raise HTTPException(status_code=404, detail=f"No access token found for {bank_name}. Please initialize bank tokens first.")

    try:
        consent_id = await bank_client.create_consent(access_token, permissions, user_id)
        return {"message": "Consent created successfully.", "consent_id": consent_id}
    except httpx.HTTPStatusError as e:
        # Попытка извлечь более детальное сообщение об ошибке из ответа банка
        try:
            error_detail = e.response.json()
        except ValueError:
            error_detail = e.response.text
        raise HTTPException(status_code=e.response.status_code, detail=f"Failed to create consent for {bank_name}: {error_detail}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while creating consent for {bank_name}: {e}")
