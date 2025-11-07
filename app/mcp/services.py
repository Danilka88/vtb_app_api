from typing import List, Optional, Any
from sqlalchemy.orm import Session
from fastapi import Depends # Добавлен импорт Depends
from app.db.database import get_db
from app.utils.bank_clients import get_bank_client
from app.mcp.schemas import BankOperationResponse
from app.core.config import settings
from app.auth_manager.services import BaseAuthManager, get_auth_manager
from app.auth_manager.exceptions import TokenFetchError
import asyncio
import httpx

class MCPService:
    """
    Сервис для координации мультибанковых операций.
    Абстрагирует взаимодействие с отдельными банками и предоставляет унифицированный интерфейс.
    """
    def __init__(self, db: Session, auth_manager: BaseAuthManager):
        self.db = db
        self.auth_manager = auth_manager

    async def _execute_bank_operation(self, bank_name: str, user_id: str, operation_func) -> BankOperationResponse:
        """
        Вспомогательный метод для выполнения операции с конкретным банком.
        Обрабатывает получение токена, вызов операции и обработку ошибок.
        """
        try:
            access_token = await self.auth_manager.get_access_token(self.db, bank_name)
            bank_client = get_bank_client(bank_name)
            
            result = await operation_func(bank_client, access_token)
            return BankOperationResponse(
                bank_name=bank_name,
                status="success",
                data=result
            )
        except TokenFetchError as e:
            return BankOperationResponse(
                bank_name=bank_name,
                status="failed",
                message=f"Не удалось получить токен доступа для банка {bank_name}: {e.details}",
                error="TOKEN_FETCH_ERROR"
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

    async def get_all_accounts(self, bank_names: List[str], user_id: str, consent_id: Optional[str] = None) -> List[BankOperationResponse]:
        """
        Получает счета из указанных банков для заданного пользователя.
        Требует `consent_id`, если он не будет получен автоматически в будущем.
        """
        tasks = []
        for bank_name in bank_names:
            # В будущем MCP должен будет сам находить или создавать consent_id.
            # Пока что мы требуем его передачи.
            if not consent_id:
                # Создаем задачу, которая сразу вернет ошибку, если consent_id не предоставлен.
                async def create_error_task():
                    return BankOperationResponse(
                        bank_name=bank_name,
                        status="failed",
                        message=f"Для получения счетов из банка {bank_name} требуется consent_id.",
                        error="CONSENT_ID_REQUIRED"
                    )
                tasks.append(create_error_task())
                continue

            tasks.append(self._execute_bank_operation(
                bank_name,
                user_id,
                lambda client, token: client.accounts.get_accounts(token, consent_id, user_id)
            ))
        results = await asyncio.gather(*tasks)
        return results

    async def get_transactions_for_account(self, bank_name: str, user_id: str, consent_id: str, account_id: str) -> List[Any]:
        """
        Заглушка для получения транзакций для конкретного счета.
        В реальной реализации будет вызывать соответствующий метод клиента банка.
        """
        # Здесь должна быть реальная логика вызова клиента банка
        # Например:
        # access_token = await self.auth_manager.get_access_token(self.db, bank_name)
        # bank_client = get_bank_client(bank_name)
        # transactions = await bank_client.data.get_transactions(access_token, consent_id, user_id, account_id)
        # return transactions
        
        # Для целей тестирования и пока нет реальной реализации
        # возвращаем пустой список или моковые данные
        return []

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

def get_mcp_service(
    db: Session = Depends(get_db),
    auth_manager: BaseAuthManager = Depends(get_auth_manager)
) -> MCPService:
    """
    Зависимость для предоставления экземпляра MCPService.
    """
    return MCPService(db=db, auth_manager=auth_manager)

def _raise_consent_error(bank_name: str):
    raise ValueError(f"Для получения счетов из банка {bank_name} требуется consent_id. MCP должен управлять согласиями.")