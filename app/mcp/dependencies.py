from sqlalchemy.orm import Session
from fastapi import Depends
from app.db.database import get_db
from app.mcp.services import MCPService
from app.auth_manager.dependencies import get_auth_manager
from app.auth_manager.services import BaseAuthManager

def get_mcp_service(
    db: Session = Depends(get_db),
    auth_manager: BaseAuthManager = Depends(get_auth_manager)
) -> MCPService:
    """
    Зависимость FastAPI для получения экземпляра MCPService.
    Корректно инициализирует сервис с зависимостями от БД и AuthManager.
    """
    return MCPService(db=db, auth_manager=auth_manager)