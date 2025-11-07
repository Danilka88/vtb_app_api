from pydantic import BaseModel, Field
from typing import List

class TokenResponse(BaseModel):
    """
    Стандартная модель ответа для запроса токена по OAuth 2.0.
    """
    access_token: str = Field(..., description="Токен доступа")
    expires_in: int = Field(..., description="Время жизни токена в секундах")
    token_type: str = Field("Bearer", description="Тип токена")
    scope: str | None = None

class JWK(BaseModel):
    """
    Модель для JSON Web Key (JWK).
    """
    kty: str
    use: str
    kid: str
    alg: str
    n: str
    e: str

class JWKSet(BaseModel):
    """
    Модель для набора JSON Web Key (JWKS).
    """
    keys: List[JWK]
