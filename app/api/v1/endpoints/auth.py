from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
import httpx

from app.core.config import settings
from app.db import crud
from app.db.database import get_db
from app.banks.vbank_client import VBankClient
from app.banks.abank_client import ABankClient
from app.banks.sbank_client import SBankClient
from app.utils.bank_clients import get_bank_client

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
    user_id: str # Идентификатор пользователя, для которого запрашивается согласие (например, team042-1 до team042-10)
    debtor_account: str | None = None # Идентификатор счета дебитора (счета списания). Обязателен для платежных согласий.
    amount: str | None = None # Сумма платежа. Обязательна для платежных согласий.
    expiration_date: str | None = None
    transaction_from_date: str | None = None
    transaction_to_date: str | None = None



@router.post("/init-bank-tokens")
async def init_bank_tokens(db: Session = Depends(get_db)):
    """
    Инициализирует и сохраняет токены доступа для всех поддерживаемых банков.
    Использует упрощенный поток получения `bank-token` для каждого банка.
    Эти токены необходимы для дальнейшего взаимодействия с API банков (например, для создания согласий).
    """
    bank_clients = {
        "vbank": VBankClient(client_id=settings.CLIENT_ID, client_secret=settings.CLIENT_SECRET, api_url=settings.VBANK_API_URL),
        "abank": ABankClient(client_id=settings.CLIENT_ID, client_secret=settings.CLIENT_SECRET, api_url=settings.ABANK_API_URL),
        "sbank": SBankClient(client_id=settings.CLIENT_ID, client_secret=settings.CLIENT_SECRET, api_url=settings.SBANK_API_URL),
    }

    for bank_name, bank_client in bank_clients.items():
        try:
            token_data = await bank_client.get_bank_token()
            crud.save_token(
                db=db,
                bank_name=bank_name,
                token=token_data["access_token"],
                expires_in=token_data["expires_in"]
            )
        except Exception as e:
            # Логируем ошибку для отладки, но пользователю возвращаем более общее сообщение
            raise HTTPException(status_code=500, detail=f"Не удалось получить токен для банка {bank_name}: {e}")

    return {"message": "Токены банков успешно инициализированы."}

@router.post("/create-consent")
async def create_consent(request: ConsentRequest, db: Session = Depends(get_db)):
    """
    Создает согласие для указанного банка с заданными разрешениями.
    Этот эндпоинт универсален и может создавать как согласия на доступ к счетам,
    так и согласия на выполнение платежей, в зависимости от переданных разрешений.

    - Если в `permissions` присутствует `CreateDomesticSinglePayment`, создается платежное согласие.
      Для платежного согласия требуются `debtor_account` (идентификатор счета дебитора) и `amount`.
    - В противном случае создается согласие на доступ к данным счетов.

    Возвращает `consent_id`, который затем используется для запросов данных или инициирования платежей.
    """
    bank_name = request.bank_name.lower()
    permissions = request.permissions
    user_id = request.user_id

    # Инициализация клиента банка в зависимости от имени банка
    if bank_name == "vbank":
        bank_client = VBankClient(client_id=settings.CLIENT_ID, client_secret=settings.CLIENT_SECRET, api_url=settings.VBANK_API_URL)
    elif bank_name == "abank":
        bank_client = ABankClient(client_id=settings.CLIENT_ID, client_secret=settings.CLIENT_SECRET, api_url=settings.ABANK_API_URL)
    elif bank_name == "sbank":
        bank_client = SBankClient(client_id=settings.CLIENT_ID, client_secret=settings.CLIENT_SECRET, api_url=settings.SBANK_API_URL)
    else:
        raise HTTPException(status_code=400, detail="Неподдерживаемый банк.")

    # Получение токена доступа из базы данных
    access_token = crud.get_decrypted_token(db, bank_name)
    if not access_token:
        raise HTTPException(status_code=404, detail=f"Токен доступа для банка {bank_name} не найден. Пожалуйста, сначала инициализируйте токены банков.")

    try:
        # Проверка на тип согласия: платежное или на доступ к данным
        if "CreateDomesticSinglePayment" in permissions:
            # Для платежного согласия требуются debtor_account и amount
            if not request.debtor_account or not request.amount:
                raise HTTPException(status_code=400, detail="Для платежного согласия требуются 'debtor_account' и 'amount'.")
            consent_id = await bank_client.create_payment_consent(access_token, permissions, user_id, settings.CLIENT_ID, request.debtor_account, request.amount, currency="RUB")
        else:
            # Создание согласия на доступ к данным
            consent_id = await bank_client.create_consent(access_token, permissions, user_id)
        return {"message": "Согласие успешно создано.", "consent_id": consent_id}
    except httpx.HTTPStatusError as e:
        # Обработка ошибок HTTP, полученных от API банка
        try:
            error_detail = e.response.json()
        except ValueError:
            error_detail = e.response.text
        raise HTTPException(status_code=e.response.status_code, detail=f"Не удалось создать согласие для банка {bank_name}: {error_detail}")
    except Exception as e:
        # Обработка любых других непредвиденных ошибок
        raise HTTPException(status_code=500, detail=f"Произошла непредвиденная ошибка при создании согласия для банка {bank_name}: {e}")


@router.get("/consents/{consent_id}")
async def get_consent_details(consent_id: str, bank_name: str = Query(..., description="Название банка (например, 'vbank')"), user_id: str = Query(..., description="Идентификатор пользователя"), db: Session = Depends(get_db)):
    """
    Получает детали согласия по его ID.
    """
    bank_client = get_bank_client(bank_name.lower())
    access_token = crud.get_decrypted_token(db, bank_name.lower())
    if not access_token:
        raise HTTPException(status_code=404, detail=f"Токен доступа для банка {bank_name} не найден.")

    try:
        consent_details = await bank_client.get_consent(access_token, consent_id, user_id)
        return {"message": "Детали согласия успешно получены.", "details": consent_details}
    except NotImplementedError:
        raise HTTPException(status_code=501, detail=f"Получение деталей согласия не реализовано для банка {bank_name}.")
    except httpx.HTTPStatusError as e:
        try:
            error_detail = e.response.json()
        except ValueError:
            error_detail = e.response.text
        raise HTTPException(status_code=e.response.status_code, detail=f"Не удалось получить детали согласия для банка {bank_name}: {error_detail}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Произошла непредвиденная ошибка при получении деталей согласия для банка {bank_name}: {e}")


@router.delete("/consents/{consent_id}")
async def revoke_consent(consent_id: str, bank_name: str = Query(..., description="Название банка (например, 'vbank')"), user_id: str = Query(..., description="Идентификатор пользователя"), db: Session = Depends(get_db)):
    """
    Отзывает согласие по его ID.
    """
    bank_client = get_bank_client(bank_name.lower())
    access_token = crud.get_decrypted_token(db, bank_name.lower())
    if not access_token:
        raise HTTPException(status_code=404, detail=f"Токен доступа для банка {bank_name} не найден.")

    try:
        revoke_result = await bank_client.revoke_consent(access_token, consent_id, user_id)
        return {"message": "Согласие успешно отозвано.", "details": revoke_result}
    except NotImplementedError:
        raise HTTPException(status_code=501, detail=f"Отзыв согласия не реализован для банка {bank_name}.")
    except httpx.HTTPStatusError as e:
        try:
            error_detail = e.response.json()
        except ValueError:
            error_detail = e.response.text
        raise HTTPException(status_code=e.response.status_code, detail=f"Не удалось отозвать согласие для банка {bank_name}: {error_detail}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Произошла непредвиденная ошибка при отзыве согласия для банка {bank_name}: {e}")
