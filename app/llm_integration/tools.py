from langchain.tools import tool
from app.db.database import get_db
from app.db import crud
from app.core.config import settings
from app.utils.bank_clients import get_bank_client
from app.mcp.services import MCPService
from app.mcp.schemas import MultiBankAccountsRequest
from sqlalchemy.orm import Session
import httpx

# Временное решение: для получения db сессии вне FastAPI контекста
# В реальном приложении это может быть реализовано через Dependency Injection
def get_db_session():
    db_gen = get_db()
    db = next(db_gen)
    try:
        yield db
    finally:
        db.close()

@tool
async def get_all_accounts_from_mcp(user_id: str, bank_names: list[str]) -> str:
    """
    Получает информацию о счетах пользователя из нескольких банков через MCP.
    Используйте этот инструмент, когда пользователь запрашивает информацию о своих счетах.
    Входные параметры:
    - user_id (str): Идентификатор пользователя.
    - bank_names (list[str]): Список названий банков (например, ['vbank', 'abank']).
    """
    db: Session = next(get_db_session())
    mcp_service = MCPService(db=db)
    request = MultiBankAccountsRequest(user_id=user_id, bank_names=bank_names)
    results = await mcp_service.get_all_accounts(request.bank_names, request.user_id)
    return str(results)

# TODO: Добавить другие инструменты для взаимодействия с API (транзакции, балансы, платежи, продукты)
