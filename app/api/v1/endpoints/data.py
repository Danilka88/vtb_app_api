from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
import httpx

from app.core.config import settings
from app.db import crud
from app.db.database import get_db
from app.utils.bank_clients import get_bank_client
from app.schemas.account import AccountCreateRequest, AccountDetailsRequest, AccountStatusUpdateRequest, AccountCloseRequest

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



@router.post("/accounts")
async def create_account(request: AccountCreateRequest, bank_name: str = Query(..., description="Название банка (например, 'vbank')"), db: Session = Depends(get_db)):
    """
    Создает новый счет для пользователя в указанном банке.
    """
    bank_name = bank_name.lower()

    bank_client = get_bank_client(bank_name)

    access_token = crud.get_decrypted_token(db, bank_name)
    if not access_token:
        raise HTTPException(status_code=404, detail=f"Токен доступа для банка {bank_name} не найден. Пожалуйста, сначала инициализируйте токены банков.")

    try:
        account_data = request.model_dump()
        new_account = await bank_client.accounts.create_account(access_token, account_data)
        return {"message": "Счет успешно создан.", "account": new_account}
    except httpx.HTTPStatusError as e:
        try:
            error_detail = e.response.json()
        except ValueError:
            error_detail = e.response.text
        raise HTTPException(status_code=e.response.status_code, detail=f"Не удалось создать счет для банка {bank_name}: {error_detail}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Произошла непредвиденная ошибка при создании счета для банка {bank_name}: {e}")


@router.post("/accounts/list")
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


@router.get("/accounts/{account_id}")
async def get_account_details(account_id: str, request: AccountDetailsRequest = Depends(), db: Session = Depends(get_db)):
    """
    Получает детальную информацию о конкретном счете.
    """
    bank_name = request.bank_name.lower()
    consent_id = request.consent_id
    user_id = request.user_id

    bank_client = get_bank_client(bank_name)

    access_token = crud.get_decrypted_token(db, bank_name)
    if not access_token:
        raise HTTPException(status_code=404, detail=f"Токен доступа для банка {bank_name} не найден. Пожалуйста, сначала инициализируйте токены банков.")

    try:
        account_details = await bank_client.accounts.get_account_details(access_token, consent_id, user_id, account_id)
        return {"message": "Детали счета успешно получены.", "account": account_details}
    except httpx.HTTPStatusError as e:
        try:
            error_detail = e.response.json()
        except ValueError:
            error_detail = e.response.text
        raise HTTPException(status_code=e.response.status_code, detail=f"Не удалось получить детали счета для банка {bank_name}: {error_detail}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Произошла непредвиденная ошибка при получении деталей счета для банка {bank_name}: {e}")


@router.put("/accounts/{account_id}/status")
async def update_account_status(account_id: str, request: AccountStatusUpdateRequest, db: Session = Depends(get_db)):
    """
    Изменяет статус счета пользователя.
    """
    bank_name = request.bank_name.lower()
    user_id = request.user_id
    status = request.status

    bank_client = get_bank_client(bank_name)

    access_token = crud.get_decrypted_token(db, bank_name)
    if not access_token:
        raise HTTPException(status_code=404, detail=f"Токен доступа для банка {bank_name} не найден. Пожалуйста, сначала инициализируйте токены банков.")

    try:
        updated_account = await bank_client.accounts.update_account_status(access_token, user_id, account_id, status)
        return {"message": "Статус счета успешно обновлен.", "account": updated_account}
    except httpx.HTTPStatusError as e:
        try:
            error_detail = e.response.json()
        except ValueError:
            error_detail = e.response.text
        raise HTTPException(status_code=e.response.status_code, detail=f"Не удалось обновить статус счета для банка {bank_name}: {error_detail}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Произошла непредвиденная ошибка при обновлении статуса счета для банка {bank_name}: {e}")


@router.put("/accounts/{account_id}/close")
async def close_account(account_id: str, request: AccountCloseRequest, db: Session = Depends(get_db)):
    """
    Закрывает счет пользователя.
    """
    bank_name = request.bank_name.lower()
    user_id = request.user_id

    bank_client = get_bank_client(bank_name)

    access_token = crud.get_decrypted_token(db, bank_name)
    if not access_token:
        raise HTTPException(status_code=404, detail=f"Токен доступа для банка {bank_name} не найден. Пожалуйста, сначала инициализируйте токены банков.")

    try:
        closed_account = await bank_client.accounts.close_account(access_token, user_id, account_id)
        return {"message": "Счет успешно закрыт.", "account": closed_account}
    except httpx.HTTPStatusError as e:
        try:
            error_detail = e.response.json()
        except ValueError:
            error_detail = e.response.text
        raise HTTPException(status_code=e.response.status_code, detail=f"Не удалось закрыть счет для банка {bank_name}: {error_detail}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Произошла непредвиденная ошибка при закрытии счета для банка {bank_name}: {e}")


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
