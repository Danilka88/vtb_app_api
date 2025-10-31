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


class AccountsRequest(BaseModel):
    bank_name: str
    consent_id: str
    user_id: str # Идентификатор пользователя, например, team042-1


class BalancesRequest(BaseModel):
    bank_name: str
    consent_id: str
    user_id: str


class TransactionsRequest(BaseModel):
    bank_name: str
    consent_id: str
    user_id: str


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_bank_client(bank_name: str):
    if bank_name == "vbank":
        return VBankClient(client_id=settings.CLIENT_ID, client_secret=settings.CLIENT_SECRET, api_url=settings.VBANK_API_URL)
    elif bank_name == "abank":
        return ABankClient(client_id=settings.CLIENT_ID, client_secret=settings.CLIENT_SECRET, api_url=settings.ABANK_API_URL)
    elif bank_name == "sbank":
        return SBankClient(client_id=settings.CLIENT_ID, client_secret=settings.CLIENT_SECRET, api_url=settings.SBANK_API_URL)
    else:
        raise HTTPException(status_code=400, detail="Unsupported bank.")


@router.post("/accounts")
async def get_accounts(request: AccountsRequest, db: Session = Depends(get_db)):
    """
    Fetches accounts for a given bank using a consent ID.
    """
    bank_name = request.bank_name.lower()
    consent_id = request.consent_id
    user_id = request.user_id

    bank_client = get_bank_client(bank_name)

    access_token = crud.get_decrypted_token(db, bank_name)
    if not access_token:
        raise HTTPException(status_code=404, detail=f"No access token found for {bank_name}. Please initialize bank tokens first.")

    try:
        accounts = await bank_client.get_accounts(access_token, consent_id, user_id)
        return {"message": "Accounts fetched successfully.", "accounts": accounts}
    except httpx.HTTPStatusError as e:
        # Попытка извлечь более детальное сообщение об ошибке из ответа банка
        try:
            error_detail = e.response.json()
        except ValueError:
            error_detail = e.response.text
        raise HTTPException(status_code=e.response.status_code, detail=f"Failed to fetch accounts for {bank_name}: {error_detail}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while fetching accounts for {bank_name}: {e}")


@router.post("/accounts/{account_id}/balances")
async def get_account_balances(account_id: str, request: BalancesRequest, db: Session = Depends(get_db)):
    """
    Fetches balances for a specific account using a consent ID.
    """
    bank_name = request.bank_name.lower()
    consent_id = request.consent_id
    user_id = request.user_id

    bank_client = get_bank_client(bank_name)

    access_token = crud.get_decrypted_token(db, bank_name)
    if not access_token:
        raise HTTPException(status_code=404, detail=f"No access token found for {bank_name}. Please initialize bank tokens first.")

    try:
        balances = await bank_client.get_account_balances(access_token, consent_id, user_id, account_id)
        return {"message": "Balances fetched successfully.", "balances": balances}
    except httpx.HTTPStatusError as e:
        try:
            error_detail = e.response.json()
        except ValueError:
            error_detail = e.response.text
        raise HTTPException(status_code=e.response.status_code, detail=f"Failed to fetch balances for {bank_name}: {error_detail}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while fetching balances for {bank_name}: {e}")


@router.post("/accounts/{account_id}/transactions")
async def get_account_transactions(account_id: str, request: TransactionsRequest, db: Session = Depends(get_db)):
    """
    Fetches transactions for a specific account using a consent ID.
    """
    bank_name = request.bank_name.lower()
    consent_id = request.consent_id
    user_id = request.user_id

    bank_client = get_bank_client(bank_name)

    access_token = crud.get_decrypted_token(db, bank_name)
    if not access_token:
        raise HTTPException(status_code=404, detail=f"No access token found for {bank_name}. Please initialize bank tokens first.")

    try:
        transactions = await bank_client.get_account_transactions(access_token, consent_id, user_id, account_id)
        return {"message": "Transactions fetched successfully.", "transactions": transactions}
    except httpx.HTTPStatusError as e:
        try:
            error_detail = e.response.json()
        except ValueError:
            error_detail = e.response.text
        raise HTTPException(status_code=e.response.status_code, detail=f"Failed to fetch transactions for {bank_name}: {error_detail}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while fetching transactions for {bank_name}: {e}")
