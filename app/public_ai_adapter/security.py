from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

from app.core.config import settings

API_KEY_HEADER = APIKeyHeader(name="X-API-Key")

async def get_api_key(api_key_header: str = Security(API_KEY_HEADER)):
    """
    Проверяет, соответствует ли переданный в заголовке X-API-Key ключ
    тому, что указан в переменной окружения PUBLIC_ADAPTER_API_KEY.
    """
    if not settings.PUBLIC_ADAPTER_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API Key for the adapter is not configured on the server."
        )
    
    if api_key_header == settings.PUBLIC_ADAPTER_API_KEY:
        return api_key_header
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials."
        )
