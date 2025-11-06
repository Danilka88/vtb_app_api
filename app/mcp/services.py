from typing import List, Optional, Any
from sqlalchemy.orm import Session
from app.db import crud
from app.utils.bank_clients import get_bank_client
from app.mcp.schemas import BankOperationResponse
from app.core.config import settings
import asyncio
import httpx

class MCPService:
    """
    Сервис для координации мультибанковых операций.
    Абстрагирует взаимодействие с отдельными банками и предоставляет унифицированный интерфейс.
    """
    def __init__(self, db: Session):
        self.db = db

    async def _execute_bank_operation(self, bank_name: str, user_id: str, operation_func) -> BankOperationResponse:
        """
        Вспомогательный метод для выполнения операции с конкретным банком.
        Обрабатывает получение токена, вызов операции и обработку ошибок.
        """
        try:
            bank_client = get_bank_client(bank_name)
            # В будущем здесь будет логика получения access_token через OAuth
            # Пока используем существующий crud.get_decrypted_token
            access_token = crud.get_decrypted_token(self.db, bank_name)
            if not access_token:
                return BankOperationResponse(
                    bank_name=bank_name,
                    status="failed",
                    message=f"Токен доступа для банка {bank_name} не найден.",
                    error="TOKEN_NOT_FOUND"
                )
            
            result = await operation_func(bank_client, access_token)
            return BankOperationResponse(
                bank_name=bank_name,
                status="success",
                data=result
            )
        except httpx.HTTPStatusError as e:
            try:
                error_detail = e.response.json()
            except ValueError:
                error_detail = e.response.text
            return BankOperationResponse(
                bank_name=bank_name,
                status="failed",
                message=f"Ошибка HTTP от банка {bank_name}: {error_detail}",
                error=str(e.response.status_code)
            )
        except Exception as e:
            return BankOperationResponse(
                bank_name=bank_name,
                status="failed",
                message=f"Непредвиденная ошибка при работе с банком {bank_name}: {e}",
                error=str(e)
            )

    async def get_all_accounts(self, bank_names: List[str], user_id: str) -> List[BankOperationResponse]:
        """
        Получает счета из указанных банков для заданного пользователя.
        """
        tasks = []
        for bank_name in bank_names:
            # Для получения счетов нужен consent_id. В текущей реализации он получается отдельно.
            # Здесь мы предполагаем, что consent_id либо уже есть, либо его нужно будет получить.
            # Для простоты пока будем использовать заглушку или требовать его в запросе.
            # В реальной системе MCP должен управлять согласиями.
            # Пока что, для демонстрации, будем использовать заглушку для consent_id.
            # В будущем MCP должен будет сам запрашивать или получать consent_id.
            # Для текущей реализации, чтобы не менять существующий функционал, 
            # мы будем использовать заглушку или требовать consent_id в запросе к MCP.
            # Но для get_all_accounts, если мы хотим получить все счета, нам нужно будет 
            # либо иметь consent_id для каждого банка, либо реализовать логику его получения.
            # Для начала, давайте сделаем упрощенную версию, которая будет пытаться получить счета
            # и возвращать ошибку, если consent_id не найден или не передан.

            # Временное решение: для получения счетов, MCP должен будет иметь доступ к consent_id.
            # Поскольку текущий crud.get_decrypted_token не хранит consent_id, 
            # мы не можем его получить здесь. Это указывает на необходимость доработки 
            # модели хранения токенов и согласий.
            # Для демонстрации функционала MCP, пока что, этот метод будет возвращать ошибку,
            # если consent_id не может быть получен.

            # TODO: Реализовать получение consent_id для каждого банка и пользователя.
            # Это потребует доработки модели Token в app/db/models.py для хранения consent_id.
            # Или же MCP должен будет сам инициировать создание согласия, если его нет.

            # Для текущей демонстрации, мы просто вернем ошибку, если consent_id не доступен.
            # В реальной системе MCP должен будет управлять жизненным циклом согласий.

            # Заглушка для consent_id, пока не будет реализовано управление согласиями в MCP
            # Это место, где MCP должен будет получить или создать consent_id
            # Для текущего примера, мы просто передадим None и обработаем ошибку.
            consent_id = None # Здесь должна быть логика получения consent_id

            tasks.append(self._execute_bank_operation(
                bank_name,
                user_id,
                lambda client, token, current_bank_name=bank_name: client.accounts.get_accounts(token, consent_id, user_id) if consent_id else _raise_consent_error(current_bank_name)
            ))
        results = await asyncio.gather(*tasks)
        return results

    async def create_bank_consent(self, bank_name: str, permissions: List[str], user_id: str, debtor_account: Optional[str] = None, amount: Optional[str] = None, currency: str = "RUB") -> BankOperationResponse:
        """
        Создает согласие для указанного банка.
        """
        return await self._execute_bank_operation(
            bank_name,
            user_id,
            lambda client, token: client.create_payment_consent(token, permissions, user_id, settings.CLIENT_ID, debtor_account, amount, currency) 
                if "CreateDomesticSinglePayment" in permissions and debtor_account and amount 
                else client.create_consent(token, permissions, user_id)
        )

def _raise_consent_error(bank_name: str):
    raise ValueError(f"Для получения счетов из банка {bank_name} требуется consent_id. MCP должен управлять согласиями.")
