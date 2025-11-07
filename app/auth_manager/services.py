from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import Dict, Any
import httpx
from sqlalchemy.orm import Session
from jose import jwt, jwk
from jose.exceptions import JWTError
from fastapi import Depends

from app.core.config import settings
from app.db import crud
from app.auth_manager.exceptions import TokenFetchError, JWKSFetchError, JWTVerificationError
from app.auth_manager.schemas import TokenResponse

# Простой in-memory кэш для токенов {bank_name: (token, expiry_time)}
_token_cache: Dict[str, tuple[str, datetime]] = {}
# Простой in-memory кэш для JWKS {bank_api_url: jwks_dict}
_jwks_cache: Dict[str, Dict[str, Any]] = {}


class BaseAuthManager(ABC):
    """
    Абстрактный базовый класс для менеджера аутентификации.
    Определяет контракт для получения токенов доступа и валидации JWT.
    """

    @abstractmethod
    async def get_access_token(self, db: Session, bank_name: str) -> str:
        """
        Получает валидный токен доступа для указанного банка.
        """
        pass

    @abstractmethod
    async def verify_jwt(self, token: str, bank_api_url: str) -> dict:
        """
        Проверяет JWT, используя соответствующий JWKS.
        """
        pass


class OAuth2AuthManager(BaseAuthManager):
    """
    Реализация менеджера аутентификации, использующая OAuth 2.0 и JWKS.
    """

    async def get_access_token(self, db: Session, bank_name: str) -> str:
        """
        Получает токен, используя каскадную логику: кэш -> новый запрос.
        """
        cached_token = _token_cache.get(bank_name)
        if cached_token:
            token, expiry = cached_token
            if expiry > datetime.now(timezone.utc):
                return token

        return await self._fetch_and_cache_new_token(db, bank_name)

    async def _fetch_and_cache_new_token(self, db: Session, bank_name: str) -> str:
        """
        Выполняет запрос на получение нового токена и кэширует его.
        """
        auth_url = settings.BANK_AUTH_URL
        if not auth_url:
            raise TokenFetchError(bank_name, "URL для аутентификации не настроен в .env (BANK_AUTH_URL)")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    auth_url,
                    data={
                        "grant_type": "client_credentials",
                        "client_id": settings.CLIENT_ID,
                        "client_secret": settings.CLIENT_SECRET,
                    }
                )
                response.raise_for_status()
                token_data = TokenResponse(**response.json())

        except httpx.HTTPStatusError as e:
            raise TokenFetchError(bank_name, f"HTTP error {e.response.status_code}: {e.response.text}")
        except Exception as e:
            raise TokenFetchError(bank_name, f"An unexpected error occurred: {str(e)}")

        crud.save_token(
            db=db,
            bank_name=bank_name,
            token=token_data.access_token,
            expires_in=token_data.expires_in
        )

        expiry_time = datetime.now(timezone.utc) + timedelta(seconds=token_data.expires_in - 60)
        _token_cache[bank_name] = (token_data.access_token, expiry_time)

        return token_data.access_token

    async def _get_jwks(self, bank_api_url: str) -> Dict[str, Any]:
        """
        Получает и кэширует JWKS от банка.
        """
        if bank_api_url in _jwks_cache:
            return _jwks_cache[bank_api_url]

        jwks_url = f"{bank_api_url}/.well-known/jwks.json"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(jwks_url)
                response.raise_for_status()
                jwks = response.json()
                _jwks_cache[bank_api_url] = jwks
                return jwks
        except httpx.HTTPStatusError as e:
            raise JWKSFetchError(f"Failed to fetch JWKS from {jwks_url}. Status: {e.response.status_code}")
        except Exception as e:
            raise JWKSFetchError(f"An unexpected error occurred while fetching JWKS from {jwks_url}: {e}")

    async def verify_jwt(self, token: str, bank_api_url: str) -> dict:
        """
        Проверяет подпись и срок действия JWT токена.
        """
        try:
            jwks = await self._get_jwks(bank_api_url)
            unverified_header = jwt.get_unverified_header(token)
            rsa_key = {}
            for key in jwks["keys"]:
                if key["kid"] == unverified_header["kid"]:
                    rsa_key = {
                        "kty": key["kty"],
                        "kid": key["kid"],
                        "use": key["use"],
                        "n": key["n"],
                        "e": key["e"]
                    }
            if not rsa_key:
                raise JWTVerificationError("Unable to find appropriate key in JWKS")

            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=["RS256"],
                options={"verify_aud": False} # Аудиторию можно будет добавить в будущем
            )
            return payload
        except JWTError as e:
            raise JWTVerificationError(f"JWT validation failed: {e}")
        except Exception as e:
            raise JWTVerificationError(f"An unexpected error occurred during JWT verification: {e}")

    async def clear_cache(self, bank_name: str):
        """
        Очищает кэш токенов для указанного банка.
        """
        if bank_name in _token_cache:
            del _token_cache[bank_name]

def get_auth_manager() -> BaseAuthManager:
    """
    Зависимость для предоставления экземпляра BaseAuthManager.
    """
    return OAuth2AuthManager()