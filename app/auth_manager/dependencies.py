from sqlalchemy.orm import Session
from fastapi import Depends

from app.db.database import get_db
from app.auth_manager.services import BaseAuthManager, OAuth2AuthManager

# Экземпляр менеджера создается один раз и переиспользуется
# Это позволяет эффективно использовать in-memory кэш
_auth_manager_instance = OAuth2AuthManager()

def get_auth_manager() -> BaseAuthManager:
    """
    Зависимость FastAPI для получения экземпляра AuthManager.
    Возвращает синглтон-экземпляр OAuth2AuthManager для использования кэша.
    """
    return _auth_manager_instance
