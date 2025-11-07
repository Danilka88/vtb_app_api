from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
import httpx

from app.db.database import get_db
from app.utils.bank_clients import get_bank_client
from app.schemas.account import AccountCreateRequest, AccountDetailsRequest, AccountStatusUpdateRequest, AccountCloseRequest
from app.auth_manager.dependencies import get_auth_manager
from app.auth_manager.services import BaseAuthManager
from app.auth_manager.exceptions import TokenFetchError

router = APIRouter()


class AccountsRequest(BaseModel):
    bank_name: str
    consent_id: str
    user_id: str

class BalancesRequest(BaseModel):
    bank_name: str
    consent_id: str
    user_id: str

class TransactionsRequest(BaseModel):
    bank_name: str
    consent_id: str
    user_id: str


@router.post("/accounts")
async def create_account(
    request: AccountCreateRequest,
    bank_name: str = Query(..., description="Название банка (например, 'vbank')"),
    db: Session = Depends(get_db),
    auth_manager: BaseAuthManager = Depends(get_auth_manager)
):
    """
    Создает новый счет для пользователя в указанном банке.
    """
    try:
        bank_name_lower = bank_name.lower()
        access_token = await auth_manager.get_access_token(db, bank_name_lower)
        bank_client = get_bank_client(bank_name_lower)
        
        account_data = request.model_dump()
        new_account = await bank_client.accounts.create_account(access_token, account_data)
        return {"message": "Счет успешно создан.", "account": new_account}

    except TokenFetchError as e:
        raise HTTPException(status_code=502, detail=f"Не удалось получить токен доступа: {e.details}")
    except httpx.HTTPStatusError as e:
        try:
            error_detail = e.response.json()
        except ValueError:
            error_detail = e.response.text
        raise HTTPException(status_code=e.response.status_code, detail=f"Не удалось создать счет: {error_detail}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Произошла непредвиденная ошибка: {e}")


@router.post("/accounts/list")
async def get_accounts(
    request: AccountsRequest,
    db: Session = Depends(get_db),
    auth_manager: BaseAuthManager = Depends(get_auth_manager)
):
    """
    Получает список счетов для указанного банка, используя предоставленный `consent_id`.
    """
    try:
        bank_name_lower = request.bank_name.lower()
        access_token = await auth_manager.get_access_token(db, bank_name_lower)
        bank_client = get_bank_client(bank_name_lower)

        accounts = await bank_client.accounts.get_accounts(access_token, request.consent_id, request.user_id)
        return {"message": "Счета успешно получены.", "accounts": accounts}

    except TokenFetchError as e:
        raise HTTPException(status_code=502, detail=f"Не удалось получить токен доступа: {e.details}")
    except httpx.HTTPStatusError as e:
        try:
            error_detail = e.response.json()
        except ValueError:
            error_detail = e.response.text
        raise HTTPException(status_code=e.response.status_code, detail=f"Не удалось получить счета: {error_detail}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Произошла непредвиденная ошибка: {e}")


@router.get("/accounts/{account_id}")
async def get_account_details(
    account_id: str,
    request: AccountDetailsRequest = Depends(),
    db: Session = Depends(get_db),
    auth_manager: BaseAuthManager = Depends(get_auth_manager)
):
    """
    Получает детальную информацию о конкретном счете.
    """
    try:
        bank_name_lower = request.bank_name.lower()
        access_token = await auth_manager.get_access_token(db, bank_name_lower)
        bank_client = get_bank_client(bank_name_lower)

        account_details = await bank_client.accounts.get_account_details(access_token, request.consent_id, request.user_id, account_id)
        return {"message": "Детали счета успешно получены.", "account": account_details}

    except TokenFetchError as e:
        raise HTTPException(status_code=502, detail=f"Не удалось получить токен доступа: {e.details}")
    except httpx.HTTPStatusError as e:
        try:
            error_detail = e.response.json()
        except ValueError:
            error_detail = e.response.text
        raise HTTPException(status_code=e.response.status_code, detail=f"Не удалось получить детали счета: {error_detail}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Произошла непредвиденная ошибка: {e}")


@router.put("/accounts/{account_id}/status")
async def update_account_status(
    account_id: str,
    request: AccountStatusUpdateRequest,
    db: Session = Depends(get_db),
    auth_manager: BaseAuthManager = Depends(get_auth_manager)
):
    """
    Изменяет статус счета пользователя.
    """
    try:
        bank_name_lower = request.bank_name.lower()
        access_token = await auth_manager.get_access_token(db, bank_name_lower)
        bank_client = get_bank_client(bank_name_lower)

        updated_account = await bank_client.accounts.update_account_status(access_token, request.user_id, account_id, request.status)
        return {"message": "Статус счета успешно обновлен.", "account": updated_account}

    except TokenFetchError as e:
        raise HTTPException(status_code=502, detail=f"Не удалось получить токен доступа: {e.details}")
    except httpx.HTTPStatusError as e:
        try:
            error_detail = e.response.json()
        except ValueError:
            error_detail = e.response.text
        raise HTTPException(status_code=e.response.status_code, detail=f"Не удалось обновить статус счета: {error_detail}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Произошла непредвиденная ошибка: {e}")


@router.put("/accounts/{account_id}/close")
async def close_account(
    account_id: str,
    request: AccountCloseRequest,
    db: Session = Depends(get_db),
    auth_manager: BaseAuthManager = Depends(get_auth_manager)
):
    """
    Закрывает счет пользователя.
    """
    try:
        bank_name_lower = request.bank_name.lower()
        access_token = await auth_manager.get_access_token(db, bank_name_lower)
        bank_client = get_bank_client(bank_name_lower)

        closed_account = await bank_client.accounts.close_account(access_token, request.user_id, account_id)
        return {"message": "Счет успешно закрыт.", "account": closed_account}

    except TokenFetchError as e:
        raise HTTPException(status_code=502, detail=f"Не удалось получить токен доступа: {e.details}")
    except httpx.HTTPStatusError as e:
        try:
            error_detail = e.response.json()
        except ValueError:
            error_detail = e.response.text
        raise HTTPException(status_code=e.response.status_code, detail=f"Не удалось закрыть счет: {error_detail}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Произошла непредвиденная ошибка: {e}")


@router.post("/accounts/{account_id}/balances")
async def get_account_balances(
    account_id: str,
    request: BalancesRequest,
    db: Session = Depends(get_db),
    auth_manager: BaseAuthManager = Depends(get_auth_manager)
):
    """
    Получает балансы для указанного `account_id`.
    """
    try:
        bank_name_lower = request.bank_name.lower()
        access_token = await auth_manager.get_access_token(db, bank_name_lower)
        bank_client = get_bank_client(bank_name_lower)

        balances = await bank_client.accounts.get_account_balances(access_token, request.consent_id, request.user_id, account_id)
        return {"message": "Балансы успешно получены.", "balances": balances}

    except TokenFetchError as e:
        raise HTTPException(status_code=502, detail=f"Не удалось получить токен доступа: {e.details}")
    except httpx.HTTPStatusError as e:
        try:
            error_detail = e.response.json()
        except ValueError:
            error_detail = e.response.text
        raise HTTPException(status_code=e.response.status_code, detail=f"Не удалось получить балансы: {error_detail}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Произошла непредвиденная ошибка: {e}")


@router.post("/accounts/{account_id}/transactions")
async def get_account_transactions(
    account_id: str,
    request: TransactionsRequest,
    db: Session = Depends(get_db),
    auth_manager: BaseAuthManager = Depends(get_auth_manager)
):
    """
    Получает историю транзакций для указанного `account_id`.
    """
    try:
        bank_name_lower = request.bank_name.lower()
        access_token = await auth_manager.get_access_token(db, bank_name_lower)
        bank_client = get_bank_client(bank_name_lower)

        transactions = await bank_client.accounts.get_account_transactions(access_token, request.consent_id, request.user_id, account_id)
        return {"message": "Транзакции успешно получены.", "transactions": transactions}

    except TokenFetchError as e:
        raise HTTPException(status_code=502, detail=f"Не удалось получить токен доступа: {e.details}")
    except httpx.HTTPStatusError as e:
        try:
            error_detail = e.response.json()
        except ValueError:
            error_detail = e.response.text
        raise HTTPException(status_code=e.response.status_code, detail=f"Не удалось получить транзакции: {error_detail}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Произошла непредвиденная ошибка: {e}")