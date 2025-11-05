from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import httpx

from app.core.config import settings
from app.db import crud
from app.db.database import SessionLocal
from app.banks.vbank_client import VBankClient
from app.banks.abank_client import ABankClient
from app.banks.sbank_client import SBankClient
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
import httpx

from app.core.config import settings
from app.db import crud
from app.db.database import SessionLocal
from app.banks.vbank_client import VBankClient
from app.banks.abank_client import ABankClient
from app.banks.sbank_client import SBankClient
from app.schemas.payment import PaymentInitiationRequest
from typing import Optional

router = APIRouter()

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

@router.post("/{bank_name}/create")
async def create_payment(
    bank_name: str,
    request: PaymentInitiationRequest,
    db: Session = Depends(get_db),
    consent_id: str = Header(..., alias="X-Consent-Id", description="ID согласия на платеж. Обязателен для выполнения платежа.")
):
    """
    Инициирует разовый платеж через указанный банк.

    - `bank_name`: Название банка (например, 'vbank').
    - `request`: Тело запроса, содержащее детали платежа (счета дебитора/кредитора, сумма и т.д.).
    - `consent_id`: ID предварительно полученного платежного согласия. Обязателен для успешного выполнения платежа.

    Возвращает статус и детали инициированного платежа.
    """
    bank_client = get_bank_client(bank_name.lower())
    access_token = crud.get_decrypted_token(db, bank_name.lower())

    if not access_token:
        raise HTTPException(status_code=404, detail=f"Токен доступа для банка {bank_name} не найден. Пожалуйста, сначала инициализируйте токены банков.")

    # Проверка наличия consent_id, так как он обязателен для платежей
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
        # Обработка ошибок HTTP, полученных от API банка
        try:
            error_detail = e.response.json()
        except ValueError:
            error_detail = e.response.text
        raise HTTPException(status_code=e.response.status_code, detail=f"Не удалось создать платеж для банка {bank_name}: {error_detail}")
    except Exception as e:
        # Обработка любых других непредвиденных ошибок
        raise HTTPException(status_code=500, detail=f"Произошла непредвиденная ошибка: {e}")

@router.get("/{bank_name}/{payment_id}/status")
async def get_payment_status(
    bank_name: str,
    payment_id: str,
    db: Session = Depends(get_db),
    client_id: str = Query(..., description="ID клиента (обязательно для bank_token)")
):
    """
    Получает текущий статус платежа по его идентификатору.

    - `bank_name`: Название банка (например, 'vbank').
    - `payment_id`: Идентификатор платежа, полученный при его инициировании.
    - `client_id`: Идентификатор клиента, используемый для аутентификации (например, team042).

    Возвращает статус и детали платежа.
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
        # Обработка ошибок HTTP, полученных от API банка
        try:
            error_detail = e.response.json()
        except ValueError:
            error_detail = e.response.text
        raise HTTPException(status_code=e.response.status_code, detail=f"Не удалось получить статус платежа для банка {bank_name}: {error_detail}")
    except Exception as e:
        # Обработка любых других непредвиденных ошибок
        raise HTTPException(status_code=500, detail=f"Произошла непредвиденная ошибка: {e}")
