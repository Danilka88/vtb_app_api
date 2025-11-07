from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
import httpx

from app.db.database import get_db
from app.utils.bank_clients import get_bank_client
from app.schemas.product import Product, ProductAgreement, ProductAgreementConsentRequest, ProductAgreementCreateRequest
from app.auth_manager.dependencies import get_auth_manager
from app.auth_manager.services import BaseAuthManager
from app.auth_manager.exceptions import TokenFetchError

router = APIRouter()

async def _handle_request(bank_name: str, db: Session, auth_manager: BaseAuthManager, func, *args, **kwargs):
    """Вспомогательная функция для уменьшения дублирования кода."""
    try:
        access_token = await auth_manager.get_access_token(db, bank_name.lower())
        return await func(access_token, *args, **kwargs)
    except TokenFetchError as e:
        raise HTTPException(status_code=502, detail=f"Не удалось получить токен доступа: {e.details}")
    except httpx.HTTPStatusError as e:
        try:
            error_detail = e.response.json()
        except ValueError:
            error_detail = e.response.text
        raise HTTPException(status_code=e.response.status_code, detail=f"Ошибка от API банка: {error_detail}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Произошла непредвиденная ошибка: {e}")

@router.get("/products", response_model=List[Product])
async def get_products(
    bank_name: str = Query(..., description="Название банка"),
    db: Session = Depends(get_db),
    auth_manager: BaseAuthManager = Depends(get_auth_manager)
):
    bank_client = get_bank_client(bank_name)
    return await _handle_request(bank_name, db, auth_manager, bank_client.products.get_products)

@router.get("/products/{product_id}", response_model=Product)
async def get_product_details(
    product_id: str,
    bank_name: str = Query(..., description="Название банка"),
    db: Session = Depends(get_db),
    auth_manager: BaseAuthManager = Depends(get_auth_manager)
):
    bank_client = get_bank_client(bank_name)
    return await _handle_request(bank_name, db, auth_manager, bank_client.products.get_product_details, product_id)

@router.post("/product-agreement-consents/request")
async def create_product_agreement_consent(
    request: ProductAgreementConsentRequest,
    db: Session = Depends(get_db),
    auth_manager: BaseAuthManager = Depends(get_auth_manager)
):
    bank_client = get_bank_client(request.bank_name)
    result = await _handle_request(
        request.bank_name, db, auth_manager,
        bank_client.create_product_agreement_consent,
        request.permissions, request.user_id
    )
    return {"message": "Согласие на управление договорами успешно создано.", "consent_id": result}

@router.get("/product-agreement-consents/{consent_id}")
async def get_product_agreement_consent(
    consent_id: str,
    bank_name: str = Query(..., description="Название банка"),
    user_id: str = Query(..., description="ID пользователя"),
    db: Session = Depends(get_db),
    auth_manager: BaseAuthManager = Depends(get_auth_manager)
):
    bank_client = get_bank_client(bank_name)
    return await _handle_request(
        bank_name, db, auth_manager,
        bank_client.get_product_agreement_consent,
        consent_id, user_id
    )

@router.delete("/product-agreement-consents/{consent_id}")
async def revoke_product_agreement_consent(
    consent_id: str,
    bank_name: str = Query(..., description="Название банка"),
    user_id: str = Query(..., description="ID пользователя"),
    db: Session = Depends(get_db),
    auth_manager: BaseAuthManager = Depends(get_auth_manager)
):
    bank_client = get_bank_client(bank_name)
    return await _handle_request(
        bank_name, db, auth_manager,
        bank_client.revoke_product_agreement_consent,
        consent_id, user_id
    )

@router.get("/product-agreements", response_model=List[ProductAgreement])
async def get_product_agreements(
    bank_name: str = Query(..., description="Название банка"),
    consent_id: str = Query(..., description="ID согласия"),
    user_id: str = Query(..., description="ID пользователя"),
    db: Session = Depends(get_db),
    auth_manager: BaseAuthManager = Depends(get_auth_manager)
):
    bank_client = get_bank_client(bank_name)
    return await _handle_request(
        bank_name, db, auth_manager,
        bank_client.products.get_product_agreements,
        consent_id, user_id
    )

@router.post("/product-agreements", response_model=ProductAgreement)
async def create_product_agreement(
    request: ProductAgreementCreateRequest,
    bank_name: str = Query(..., description="Название банка"),
    consent_id: str = Query(..., description="ID согласия"),
    db: Session = Depends(get_db),
    auth_manager: BaseAuthManager = Depends(get_auth_manager)
):
    bank_client = get_bank_client(bank_name)
    return await _handle_request(
        bank_name, db, auth_manager,
        bank_client.products.create_product_agreement,
        consent_id, request.user_id, request
    )

@router.get("/product-agreements/{agreement_id}", response_model=ProductAgreement)
async def get_product_agreement_details(
    agreement_id: str,
    bank_name: str = Query(..., description="Название банка"),
    consent_id: str = Query(..., description="ID согласия"),
    user_id: str = Query(..., description="ID пользователя"),
    db: Session = Depends(get_db),
    auth_manager: BaseAuthManager = Depends(get_auth_manager)
):
    bank_client = get_bank_client(bank_name)
    return await _handle_request(
        bank_name, db, auth_manager,
        bank_client.products.get_product_agreement_details,
        consent_id, user_id, agreement_id
    )

@router.delete("/product-agreements/{agreement_id}")
async def close_product_agreement(
    agreement_id: str,
    bank_name: str = Query(..., description="Название банка"),
    consent_id: str = Query(..., description="ID согласия"),
    user_id: str = Query(..., description="ID пользователя"),
    db: Session = Depends(get_db),
    auth_manager: BaseAuthManager = Depends(get_auth_manager)
):
    bank_client = get_bank_client(bank_name)
    return await _handle_request(
        bank_name, db, auth_manager,
        bank_client.products.close_product_agreement,
        consent_id, user_id, agreement_id
    )