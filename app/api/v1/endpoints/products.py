
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.db import crud
from app.utils.bank_clients import get_bank_client
from app.schemas.product import Product, ProductAgreement, ProductAgreementConsentRequest, ProductAgreementCreateRequest

router = APIRouter()

# --- Product Catalog ---

@router.get("/products", response_model=List[Product])
async def get_products(bank_name: str = Query(..., description="Название банка"), db: Session = Depends(get_db)):
    """Получает публичный каталог банковских продуктов."""
    bank_client = get_bank_client(bank_name)
    access_token = crud.get_decrypted_token(db, bank_name)
    if not access_token:
        raise HTTPException(status_code=404, detail=f"Токен для банка {bank_name} не найден.")
    return await bank_client.products.get_products(access_token)

@router.get("/products/{product_id}", response_model=Product)
async def get_product_details(product_id: str, bank_name: str = Query(..., description="Название банка"), db: Session = Depends(get_db)):
    """Получает детали конкретного продукта по его ID."""
    bank_client = get_bank_client(bank_name)
    access_token = crud.get_decrypted_token(db, bank_name)
    if not access_token:
        raise HTTPException(status_code=404, detail=f"Токен для банка {bank_name} не найден.")
    return await bank_client.products.get_product_details(access_token, product_id)

# --- Product Agreement Consents ---

@router.post("/product-agreement-consents/request")
async def create_product_agreement_consent(request: ProductAgreementConsentRequest, db: Session = Depends(get_db)):
    """Создает запрос на согласие для управления договорами по продуктам."""
    bank_client = get_bank_client(request.bank_name)
    access_token = crud.get_decrypted_token(db, request.bank_name)
    if not access_token:
        raise HTTPException(status_code=404, detail=f"Токен для банка {request.bank_name} не найден.")
    consent_id = await bank_client.create_product_agreement_consent(access_token, request.permissions, request.user_id)
    return {"message": "Согласие на управление договорами успешно создано.", "consent_id": consent_id}

@router.get("/product-agreement-consents/{consent_id}")
async def get_product_agreement_consent(
    consent_id: str, 
    bank_name: str = Query(..., description="Название банка"), 
    user_id: str = Query(..., description="ID пользователя"), 
    db: Session = Depends(get_db)
):
    """Получает детали согласия на управление договорами."""
    bank_client = get_bank_client(bank_name)
    access_token = crud.get_decrypted_token(db, bank_name)
    if not access_token:
        raise HTTPException(status_code=404, detail=f"Токен для банка {bank_name} не найден.")
    return await bank_client.get_product_agreement_consent(access_token, consent_id, user_id)

@router.delete("/product-agreement-consents/{consent_id}")
async def revoke_product_agreement_consent(
    consent_id: str, 
    bank_name: str = Query(..., description="Название банка"), 
    user_id: str = Query(..., description="ID пользователя"), 
    db: Session = Depends(get_db)
):
    """Отзывает согласие на управление договорами."""
    bank_client = get_bank_client(bank_name)
    access_token = crud.get_decrypted_token(db, bank_name)
    if not access_token:
        raise HTTPException(status_code=404, detail=f"Токен для банка {bank_name} не найден.")
    return await bank_client.revoke_product_agreement_consent(access_token, consent_id, user_id)

# --- Product Agreements ---

@router.get("/product-agreements", response_model=List[ProductAgreement])
async def get_product_agreements(
    bank_name: str = Query(..., description="Название банка"),
    consent_id: str = Query(..., description="ID согласия на управление договорами"),
    user_id: str = Query(..., description="ID пользователя"),
    db: Session = Depends(get_db)
):
    """Получает список договоров клиента по продуктам."""
    bank_client = get_bank_client(bank_name)
    access_token = crud.get_decrypted_token(db, bank_name)
    if not access_token:
        raise HTTPException(status_code=404, detail=f"Токен для банка {bank_name} не найден.")
    return await bank_client.products.get_product_agreements(access_token, consent_id, user_id)

@router.post("/product-agreements", response_model=ProductAgreement)
async def create_product_agreement(
    request: ProductAgreementCreateRequest,
    bank_name: str = Query(..., description="Название банка"),
    consent_id: str = Query(..., description="ID согласия на управление договорами"),
    db: Session = Depends(get_db)
):
    """Открывает новый продукт для клиента (создает договор)."""
    bank_client = get_bank_client(bank_name)
    access_token = crud.get_decrypted_token(db, bank_name)
    if not access_token:
        raise HTTPException(status_code=404, detail=f"Токен для банка {bank_name} не найден.")
    return await bank_client.products.create_product_agreement(access_token, consent_id, request.user_id, request)

@router.get("/product-agreements/{agreement_id}", response_model=ProductAgreement)
async def get_product_agreement_details(
    agreement_id: str,
    bank_name: str = Query(..., description="Название банка"),
    consent_id: str = Query(..., description="ID согласия на управление договорами"),
    user_id: str = Query(..., description="ID пользователя"),
    db: Session = Depends(get_db)
):
    """Получает детали конкретного договора по продукту."""
    bank_client = get_bank_client(bank_name)
    access_token = crud.get_decrypted_token(db, bank_name)
    if not access_token:
        raise HTTPException(status_code=404, detail=f"Токен для банка {bank_name} не найден.")
    return await bank_client.products.get_product_agreement_details(access_token, consent_id, user_id, agreement_id)

@router.delete("/product-agreements/{agreement_id}")
async def close_product_agreement(
    agreement_id: str,
    bank_name: str = Query(..., description="Название банка"),
    consent_id: str = Query(..., description="ID согласия на управление договорами"),
    user_id: str = Query(..., description="ID пользователя"),
    db: Session = Depends(get_db)
):
    """Закрывает (расторгает) договор по продукту."""
    bank_client = get_bank_client(bank_name)
    access_token = crud.get_decrypted_token(db, bank_name)
    if not access_token:
        raise HTTPException(status_code=404, detail=f"Токен для банка {bank_name} не найден.")
    return await bank_client.products.close_product_agreement(access_token, consent_id, user_id, agreement_id)
