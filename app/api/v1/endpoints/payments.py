from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
import httpx
from typing import Optional

from app.core.config import settings
from app.db.database import get_db
from app.utils.bank_clients import get_bank_client
from app.schemas.payment import PaymentInitiationRequest, PaymentConsentCreateRequest
from app.auth_manager.dependencies import get_auth_manager
from app.auth_manager.services import BaseAuthManager
from app.auth_manager.exceptions import TokenFetchError

router = APIRouter()


@router.post("/payment-consents")
async def create_payment_consent(
    request: PaymentConsentCreateRequest,
    db: Session = Depends(get_db),
    auth_manager: BaseAuthManager = Depends(get_auth_manager)
):
    """
    Создает новое ПЛАТЕЖНОЕ согласие.
    """
    try:
        bank_name_lower = request.bank_name.lower()
        access_token = await auth_manager.get_access_token(db, bank_name_lower)
        bank_client = get_bank_client(bank_name_lower)

        consent_id = await bank_client.create_payment_consent(
            access_token=access_token,
            permissions=request.permissions,
            user_id=request.user_id,
            requesting_bank=settings.CLIENT_ID,
            debtor_account_id=request.debtor_account,
            amount=request.amount,
            currency="RUB"
        )
        return {"message": "Платежное согласие успешно создано.", "consent_id": consent_id}

    except TokenFetchError as e:
        raise HTTPException(status_code=502, detail=f"Не удалось получить токен доступа: {e.details}")
    except httpx.HTTPStatusError as e:
        try:
            error_detail = e.response.json()
        except ValueError:
            error_detail = e.response.text
        raise HTTPException(status_code=e.response.status_code, detail=f"Не удалось создать согласие: {error_detail}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Произошла непредвиденная ошибка: {e}")


@router.post("/{bank_name}/create")
async def create_payment(
    bank_name: str,
    request: PaymentInitiationRequest,
    db: Session = Depends(get_db),
    auth_manager: BaseAuthManager = Depends(get_auth_manager),
    consent_id: str = Header(..., alias="X-Consent-Id", description="ID согласия на платеж.")
):
    """
    Инициирует разовый платеж через указанный банк.
    """
    try:
        bank_name_lower = bank_name.lower()
        access_token = await auth_manager.get_access_token(db, bank_name_lower)
        bank_client = get_bank_client(bank_name_lower)

        payment_response = await bank_client.payments.create_payment(
            access_token=access_token,
            payment_request=request,
            consent_id=consent_id
        )
        return {"message": "Платеж успешно инициирован.", "details": payment_response}

    except TokenFetchError as e:
        raise HTTPException(status_code=502, detail=f"Не удалось получить токен доступа: {e.details}")
    except NotImplementedError:
        raise HTTPException(status_code=501, detail=f"API платежей не реализован для банка {bank_name}.")
    except httpx.HTTPStatusError as e:
        try:
            error_detail = e.response.json()
        except ValueError:
            error_detail = e.response.text
        raise HTTPException(status_code=e.response.status_code, detail=f"Не удалось создать платеж: {error_detail}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Произошла непредвиденная ошибка: {e}")


@router.get("/{bank_name}/{payment_id}/status")
async def get_payment_status(
    bank_name: str,
    payment_id: str,
    client_id: str = Query(..., description="ID клиента (например, team042-1)"),
    db: Session = Depends(get_db),
    auth_manager: BaseAuthManager = Depends(get_auth_manager)
):
    """
    Получает текущий статус платежа по его идентификатору.
    """
    try:
        bank_name_lower = bank_name.lower()
        access_token = await auth_manager.get_access_token(db, bank_name_lower)
        bank_client = get_bank_client(bank_name_lower)

        status_response = await bank_client.payments.get_payment_status(access_token, payment_id, client_id)
        return {"message": "Статус платежа успешно получен.", "details": status_response}

    except TokenFetchError as e:
        raise HTTPException(status_code=502, detail=f"Не удалось получить токен доступа: {e.details}")
    except NotImplementedError:
        raise HTTPException(status_code=501, detail=f"API платежей не реализован для банка {bank_name}.")
    except httpx.HTTPStatusError as e:
        try:
            error_detail = e.response.json()
        except ValueError:
            error_detail = e.response.text
        raise HTTPException(status_code=e.response.status_code, detail=f"Не удалось получить статус платежа: {error_detail}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Произошла непредвиденная ошибка: {e}")


@router.get("/payment-consents/{consent_id}")
async def get_payment_consent_details(
    consent_id: str,
    bank_name: str = Query(..., description="Название банка"),
    user_id: str = Query(..., description="Идентификатор пользователя"),
    db: Session = Depends(get_db),
    auth_manager: BaseAuthManager = Depends(get_auth_manager)
):
    """
    Получает информацию о ПЛАТЕЖНОМ согласии по его ID.
    """
    try:
        bank_name_lower = bank_name.lower()
        access_token = await auth_manager.get_access_token(db, bank_name_lower)
        bank_client = get_bank_client(bank_name_lower)

        consent_details = await bank_client.get_payment_consent(access_token, consent_id, user_id)
        return {"message": "Детали платежного согласия успешно получены.", "details": consent_details}

    except TokenFetchError as e:
        raise HTTPException(status_code=502, detail=f"Не удалось получить токен доступа: {e.details}")
    except NotImplementedError:
        raise HTTPException(status_code=501, detail=f"Получение деталей платежного согласия не реализовано для {bank_name}.")
    except httpx.HTTPStatusError as e:
        try:
            error_detail = e.response.json()
        except ValueError:
            error_detail = e.response.text
        raise HTTPException(status_code=e.response.status_code, detail=f"Не удалось получить детали согласия: {error_detail}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Произошла непредвиденная ошибка: {e}")


@router.delete("/payment-consents/{consent_id}")
async def revoke_payment_consent(
    consent_id: str,
    bank_name: str = Query(..., description="Название банка"),
    user_id: str = Query(..., description="Идентификатор пользователя"),
    db: Session = Depends(get_db),
    auth_manager: BaseAuthManager = Depends(get_auth_manager)
):
    """
    Отзывает ПЛАТЕЖНОЕ согласие по его ID.
    """
    try:
        bank_name_lower = bank_name.lower()
        access_token = await auth_manager.get_access_token(db, bank_name_lower)
        bank_client = get_bank_client(bank_name_lower)

        revoke_result = await bank_client.revoke_payment_consent(access_token, consent_id, user_id)
        return {"message": "Платежное согласие успешно отозвано.", "details": revoke_result}

    except TokenFetchError as e:
        raise HTTPException(status_code=502, detail=f"Не удалось получить токен доступа: {e.details}")
    except NotImplementedError:
        raise HTTPException(status_code=501, detail=f"Отзыв платежного согласия не реализован для {bank_name}.")
    except httpx.HTTPStatusError as e:
        try:
            error_detail = e.response.json()
        except ValueError:
            error_detail = e.response.text
        raise HTTPException(status_code=e.response.status_code, detail=f"Не удалось отозвать согласие: {error_detail}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Произошла непредвиденная ошибка: {e}")
