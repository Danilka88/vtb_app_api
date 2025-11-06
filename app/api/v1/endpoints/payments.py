from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
import httpx
from typing import Optional

from app.core.config import settings
from app.db import crud
from app.db.database import get_db
from app.utils.bank_clients import get_bank_client
from app.schemas.payment import PaymentInitiationRequest, PaymentConsentCreateRequest

router = APIRouter()


@router.post("/payment-consents")
async def create_payment_consent(
    request: PaymentConsentCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Создает новое ПЛАТЕЖНОЕ согласие.
    """
    bank_client = get_bank_client(request.bank_name.lower())
    access_token = crud.get_decrypted_token(db, request.bank_name.lower())
    if not access_token:
        raise HTTPException(status_code=404, detail=f"Токен доступа для банка {request.bank_name} не найден.")

    try:
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
    except httpx.HTTPStatusError as e:
        try:
            error_detail = e.response.json()
        except ValueError:
            error_detail = e.response.text
        raise HTTPException(status_code=e.response.status_code, detail=f"Не удалось создать согласие для банка {request.bank_name}: {error_detail}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Произошла непредвиденная ошибка: {e}")



@router.post("/{bank_name}/create")
async def create_payment(
    bank_name: str,
    request: PaymentInitiationRequest,
    db: Session = Depends(get_db),
    consent_id: str = Header(..., alias="X-Consent-Id", description="ID согласия на платеж. Обязателен для выполнения платежа.")
):
    """
    Инициирует разовый платеж через указанный банк.
    """
    bank_client = get_bank_client(bank_name.lower())
    access_token = crud.get_decrypted_token(db, bank_name.lower())

    if not access_token:
        raise HTTPException(status_code=404, detail=f"Токен доступа для банка {bank_name} не найден.")

    if not consent_id:
        raise HTTPException(status_code=400, detail="Для инициации платежа требуется 'consent_id'.")

    try:
        payment_response = await bank_client.payments.create_payment(
            access_token=access_token,
            payment_request=request,
            consent_id=consent_id
        )
        return {"message": "Платеж успешно инициирован.", "details": payment_response}
    except NotImplementedError:
        raise HTTPException(status_code=501, detail=f"API платежей не реализован для банка {bank_name}.")
    except httpx.HTTPStatusError as e:
        try:
            error_detail = e.response.json()
        except ValueError:
            error_detail = e.response.text
        raise HTTPException(status_code=e.response.status_code, detail=f"Не удалось создать платеж для банка {bank_name}: {error_detail}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Произошла непредвиденная ошибка: {e}")


@router.get("/{bank_name}/{payment_id}/status")
async def get_payment_status(
    bank_name: str,
    payment_id: str,
    db: Session = Depends(get_db),
    client_id: str = Query(..., description="ID клиента (например, team042-1)")
):
    """
    Получает текущий статус платежа по его идентификатору.
    """
    bank_client = get_bank_client(bank_name.lower())
    access_token = crud.get_decrypted_token(db, bank_name.lower())

    if not access_token:
        raise HTTPException(status_code=404, detail=f"Токен доступа для банка {bank_name} не найден.")

    try:
        status_response = await bank_client.payments.get_payment_status(access_token, payment_id, client_id)
        return {"message": "Статус платежа успешно получен.", "details": status_response}
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
    bank_name: str = Query(..., description="Название банка (например, 'vbank')"),
    user_id: str = Query(..., description="Идентификатор пользователя"),
    db: Session = Depends(get_db)
):
    """
    Получает информацию о ПЛАТЕЖНОМ согласии по его ID.
    """
    bank_client = get_bank_client(bank_name.lower())
    access_token = crud.get_decrypted_token(db, bank_name.lower())
    if not access_token:
        raise HTTPException(status_code=404, detail=f"Токен доступа для банка {bank_name} не найден.")

    try:
        # Вызываем специализированный метод для получения платежного согласия
        consent_details = await bank_client.get_payment_consent(access_token, consent_id, user_id)
        return {"message": "Детали платежного согласия успешно получены.", "details": consent_details}
    except NotImplementedError:
        raise HTTPException(status_code=501, detail=f"Получение деталей платежного согласия не реализовано для банка {bank_name}.")
    except httpx.HTTPStatusError as e:
        try:
            error_detail = e.response.json()
        except ValueError:
            error_detail = e.response.text
        raise HTTPException(status_code=e.response.status_code, detail=f"Не удалось получить детали платежного согласия: {error_detail}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Произошла непредвиденная ошибка: {e}")


@router.delete("/payment-consents/{consent_id}")
async def revoke_payment_consent(
    consent_id: str,
    bank_name: str = Query(..., description="Название банка (например, 'vbank')"),
    user_id: str = Query(..., description="Идентификатор пользователя"),
    db: Session = Depends(get_db)
):
    """
    Отзывает ПЛАТЕЖНОЕ согласие по его ID.
    """
    bank_client = get_bank_client(bank_name.lower())
    access_token = crud.get_decrypted_token(db, bank_name.lower())
    if not access_token:
        raise HTTPException(status_code=404, detail=f"Токен доступа для банка {bank_name} не найден.")

    try:
        # Вызываем специализированный метод для отзыва платежного согласия
        revoke_result = await bank_client.revoke_payment_consent(access_token, consent_id, user_id)
        return {"message": "Платежное согласие успешно отозвано.", "details": revoke_result}
    except NotImplementedError:
        raise HTTPException(status_code=501, detail=f"Отзыв платежного согласия не реализован для банка {bank_name}.")
    except httpx.HTTPStatusError as e:
        try:
            error_detail = e.response.json()
        except ValueError:
            error_detail = e.response.text
        raise HTTPException(status_code=e.response.status_code, detail=f"Не удалось отозвать платежное согласие: {error_detail}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Произошла непредвиденная ошибка: {e}")