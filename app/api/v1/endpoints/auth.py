from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
import httpx

from app.core.config import settings
from app.db.database import get_db
from app.utils.bank_clients import get_bank_client
from app.auth_manager.dependencies import get_auth_manager
from app.auth_manager.services import BaseAuthManager
from app.auth_manager.exceptions import TokenFetchError

router = APIRouter()


class ConsentRequest(BaseModel):
    """
    Модель запроса для создания согласия на доступ к данным или на выполнение платежа.
    Определяет, какой банк, какие разрешения и для какого пользователя запрашиваются.
    """
    bank_name: str
    permissions: list[str] = [
        "ReadAccountsDetail",
        "ReadBalances",
        "ReadTransactionsCredits",
        "ReadTransactionsDebits",
        "ReadTransactionsDetail",
        "ReadBeneficiariesDetail",
        "ReadStandingOrders",
        "ReadProducts",
        "ReadOffers",
        "ReadStatements"
    ]
    user_id: str
    debtor_account: str | None = None
    amount: str | None = None
    expiration_date: str | None = None
    transaction_from_date: str | None = None
    transaction_to_date: str | None = None


@router.post("/create-consent")
async def create_consent(
    request: ConsentRequest,
    db: Session = Depends(get_db),
    auth_manager: BaseAuthManager = Depends(get_auth_manager)
):
    """
    Создает согласие для указанного банка с заданными разрешениями.
    Этот эндпоинт универсален и может создавать как согласия на доступ к счетам,
    так и согласия на выполнение платежей.
    Токен доступа получается автоматически через AuthManager.
    """
    bank_name = request.bank_name.lower()
    
    try:
        access_token = await auth_manager.get_access_token(db, bank_name)
        bank_client = get_bank_client(bank_name)

        if "CreateDomesticSinglePayment" in request.permissions:
            if not request.debtor_account or not request.amount:
                raise HTTPException(status_code=400, detail="Для платежного согласия требуются 'debtor_account' и 'amount'.")
            consent_id = await bank_client.create_payment_consent(access_token, request.permissions, request.user_id, settings.CLIENT_ID, request.debtor_account, request.amount, currency="RUB")
        else:
            consent_id = await bank_client.create_consent(access_token, request.permissions, request.user_id)
        
        return {"message": "Согласие успешно создано.", "consent_id": consent_id}
    
    except TokenFetchError as e:
        raise HTTPException(status_code=502, detail=f"Не удалось получить токен доступа: {e.details}")
    except httpx.HTTPStatusError as e:
        try:
            error_detail = e.response.json()
        except ValueError:
            error_detail = e.response.text
        raise HTTPException(status_code=e.response.status_code, detail=f"Не удалось создать согласие для банка {bank_name}: {error_detail}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Произошла непредвиденная ошибка при создании согласия для банка {bank_name}: {e}")


@router.get("/consents/{consent_id}")
async def get_consent_details(
    consent_id: str,
    bank_name: str = Query(..., description="Название банка (например, 'vbank')"),
    user_id: str = Query(..., description="Идентификатор пользователя"),
    db: Session = Depends(get_db),
    auth_manager: BaseAuthManager = Depends(get_auth_manager)
):
    """
    Получает детали согласия по его ID.
    """
    try:
        access_token = await auth_manager.get_access_token(db, bank_name.lower())
        bank_client = get_bank_client(bank_name.lower())
        
        consent_details = await bank_client.get_consent(access_token, consent_id, user_id)
        return {"message": "Детали согласия успешно получены.", "details": consent_details}

    except TokenFetchError as e:
        raise HTTPException(status_code=502, detail=f"Не удалось получить токен доступа: {e.details}")
    except NotImplementedError:
        raise HTTPException(status_code=501, detail=f"Получение деталей согласия не реализовано для банка {bank_name}.")
    except httpx.HTTPStatusError as e:
        try:
            error_detail = e.response.json()
        except ValueError:
            error_detail = e.response.text
        raise HTTPException(status_code=e.response.status_code, detail=f"Не удалось получить детали согласия: {error_detail}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Произошла непредвиденная ошибка: {e}")


@router.delete("/consents/{consent_id}")
async def revoke_consent(
    consent_id: str,
    bank_name: str = Query(..., description="Название банка (например, 'vbank')"),
    user_id: str = Query(..., description="Идентификатор пользователя"),
    db: Session = Depends(get_db),
    auth_manager: BaseAuthManager = Depends(get_auth_manager)
):
    """
    Отзывает согласие по его ID.
    """
    try:
        access_token = await auth_manager.get_access_token(db, bank_name.lower())
        bank_client = get_bank_client(bank_name.lower())

        revoke_result = await bank_client.revoke_consent(access_token, consent_id, user_id)
        return {"message": "Согласие успешно отозвано.", "details": revoke_result}

    except TokenFetchError as e:
        raise HTTPException(status_code=502, detail=f"Не удалось получить токен доступа: {e.details}")
    except NotImplementedError:
        raise HTTPException(status_code=501, detail=f"Отзыв согласия не реализован для банка {bank_name}.")
    except httpx.HTTPStatusError as e:
        try:
            error_detail = e.response.json()
        except ValueError:
            error_detail = e.response.text
        raise HTTPException(status_code=e.response.status_code, detail=f"Не удалось отозвать согласие: {error_detail}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Произошла непредвиденная ошибка: {e}")