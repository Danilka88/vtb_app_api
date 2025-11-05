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
    """
    Модель запроса для получения списка счетов пользователя.
    """
    bank_name: str
    consent_id: str
    user_id: str # Идентификатор пользователя, для которого запрашиваются счета (например, team042-1)


class BalancesRequest(BaseModel):
    """
    Модель запроса для получения балансов по конкретному счету.
    """
    bank_name: str
    consent_id: str
    user_id: str # Идентификатор пользователя, для которого запрашиваются балансы


class TransactionsRequest(BaseModel):
    """
    Модель запроса для получения истории транзакций по конкретному счету.
    """
    bank_name: str
    consent_id: str
    user_id: str # Идентификатор пользователя, для которого запрашиваются транзакции


def get_db():
    """
    Зависимость FastAPI для получения сессии базы данных.
    Создает новую сессию для каждого запроса и автоматически закрывает ее после завершения.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_bank_client(bank_name: str):
    """
    Вспомогательная функция для получения экземпляра клиента банка по его имени.
    """
    if bank_name == "vbank":
        return VBankClient(client_id=settings.CLIENT_ID, client_secret=settings.CLIENT_SECRET, api_url=settings.VBANK_API_URL)
    elif bank_name == "abank":
        return ABankClient(client_id=settings.CLIENT_ID, client_secret=settings.CLIENT_SECRET, api_url=settings.ABANK_API_URL)
    elif bank_name == "sbank":
        return SBankClient(client_id=settings.CLIENT_ID, client_secret=settings.CLIENT_SECRET, api_url=settings.SBANK_API_URL)
    else:
        raise HTTPException(status_code=400, detail="Неподдерживаемый банк.")


@router.post("/accounts")
async def get_accounts(request: AccountsRequest, db: Session = Depends(get_db)):
    """
    Получает список счетов для указанного банка, используя предоставленный `consent_id`.
    `consent_id` должен быть предварительно получен через эндпоинт `/auth/create-consent`
    с соответствующими разрешениями (например, `ReadAccountsDetail`).

    Возвращает список объектов счетов.
    """
    bank_name = request.bank_name.lower()
    consent_id = request.consent_id
    user_id = request.user_id

    bank_client = get_bank_client(bank_name)

    access_token = crud.get_decrypted_token(db, bank_name)
    if not access_token:
        raise HTTPException(status_code=404, detail=f"Токен доступа для банка {bank_name} не найден. Пожалуйста, сначала инициализируйте токены банков.")

    try:
        accounts = await bank_client.accounts.get_accounts(access_token, consent_id, user_id)
        return {"message": "Счета успешно получены.", "accounts": accounts}
    except httpx.HTTPStatusError as e:
        # Обработка ошибок HTTP, полученных от API банка
        try:
            error_detail = e.response.json()
        except ValueError:
            error_detail = e.response.text
        raise HTTPException(status_code=e.response.status_code, detail=f"Не удалось получить счета для банка {bank_name}: {error_detail}")
    except Exception as e:
        # Обработка любых других непредвиденных ошибок
        raise HTTPException(status_code=500, detail=f"Произошла непредвиденная ошибка при получении счетов для банка {bank_name}: {e}")


@router.post("/accounts/{account_id}/balances")
async def get_account_balances(account_id: str, request: BalancesRequest, db: Session = Depends(get_db)):
    """
    Получает балансы для указанного `account_id` в заданном банке, используя предоставленный `consent_id`.
    `consent_id` должен быть предварительно получен через эндпоинт `/auth/create-consent`
    с соответствующими разрешениями (например, `ReadBalances`).

    Возвращает объект с информацией о балансах счета.
    """
    bank_name = request.bank_name.lower()
    consent_id = request.consent_id
    user_id = request.user_id

    bank_client = get_bank_client(bank_name)

    access_token = crud.get_decrypted_token(db, bank_name)
    if not access_token:
        raise HTTPException(status_code=404, detail=f"Токен доступа для банка {bank_name} не найден. Пожалуйста, сначала инициализируйте токены банков.")

    try:
        balances = await bank_client.accounts.get_account_balances(access_token, consent_id, user_id, account_id)
        return {"message": "Балансы успешно получены.", "balances": balances}
    except httpx.HTTPStatusError as e:
        # Обработка ошибок HTTP, полученных от API банка
        try:
            error_detail = e.response.json()
        except ValueError:
            error_detail = e.response.text
        raise HTTPException(status_code=e.response.status_code, detail=f"Не удалось получить балансы для банка {bank_name}: {error_detail}")
    except Exception as e:
        # Обработка любых других непредвиденных ошибок
        raise HTTPException(status_code=500, detail=f"Произошла непредвиденная ошибка при получении балансов для банка {bank_name}: {e}")


@router.post("/accounts/{account_id}/transactions")
async def get_account_transactions(account_id: str, request: TransactionsRequest, db: Session = Depends(get_db)):
    """
    Получает историю транзакций для указанного `account_id` в заданном банке, используя предоставленный `consent_id`.
    `consent_id` должен быть предварительно получен через эндпоинт `/auth/create-consent`
    с соответствующими разрешениями (например, `ReadTransactionsDetail`).

    Возвращает список объектов транзакций.
    """
    bank_name = request.bank_name.lower()
    consent_id = request.consent_id
    user_id = request.user_id

    bank_client = get_bank_client(bank_name)

    access_token = crud.get_decrypted_token(db, bank_name)
    if not access_token:
        raise HTTPException(status_code=404, detail=f"Токен доступа для банка {bank_name} не найден. Пожалуйста, сначала инициализируйте токены банков.")

    try:
        transactions = await bank_client.accounts.get_account_transactions(access_token, consent_id, user_id, account_id)
        return {"message": "Транзакции успешно получены.", "transactions": transactions}
    except httpx.HTTPStatusError as e:
        # Обработка ошибок HTTP, полученных от API банка
        try:
            error_detail = e.response.json()
        except ValueError:
            error_detail = e.response.text
        raise HTTPException(status_code=e.response.status_code, detail=f"Не удалось получить транзакции для банка {bank_name}: {error_detail}")
    except Exception as e:
        # Обработка любых других непредвиденных ошибок
        raise HTTPException(status_code=500, detail=f"Произошла непредвиденная ошибка при получении транзакций для банка {bank_name}: {e}")
