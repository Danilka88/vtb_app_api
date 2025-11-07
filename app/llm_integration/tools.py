from langchain.tools import tool
from sqlalchemy.orm import Session
import httpx

from app.db.database import get_db
from app.mcp.services import MCPService
from app.mcp.schemas import MultiBankAccountsRequest
from app.auth_manager.services import OAuth2AuthManager

# Временное решение: для получения зависимостей вне FastAPI контекста
def get_deps_for_tools():
    """
    Создает и предоставляет зависимости (сессия БД, AuthManager)
    для использования в инструментах LangChain.
    """
    db_gen = get_db()
    db = next(db_gen)
    auth_manager = OAuth2AuthManager()
    try:
        yield db, auth_manager
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
    db: Session
    auth_manager: OAuth2AuthManager
    # Получаем зависимости
    deps_gen = get_deps_for_tools()
    db, auth_manager = next(deps_gen)

    try:
        mcp_service = MCPService(db=db, auth_manager=auth_manager)
        request = MultiBankAccountsRequest(user_id=user_id, bank_names=bank_names)
        results = await mcp_service.get_all_accounts(request.bank_names, request.user_id)
        return str(results)
    finally:
        # Убеждаемся, что генератор зависимостей правильно закрывается
        try:
            next(deps_gen)
        except StopIteration:
            pass

# TODO: Добавить другие инструменты для взаимодействия с API (транзакции, балансы, платежи, продукты)