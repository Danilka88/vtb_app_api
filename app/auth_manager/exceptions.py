class AuthManagerError(Exception):
    """Базовый класс для исключений в модуле аутентификации."""
    pass

class TokenFetchError(AuthManagerError):
    """Исключение, возникающее при ошибке получения токена от внешнего API."""
    def __init__(self, bank_name: str, details: str):
        self.bank_name = bank_name
        self.details = details
        super().__init__(f"Failed to fetch token for {bank_name}: {details}")

class InvalidTokenError(AuthManagerError):
    """Исключение, возникающее при попытке использовать невалидный или просроченный токен."""
    pass

class JWKSFetchError(AuthManagerError):
    """Исключение, возникающее при ошибке получения JWKS."""
    pass

class JWTVerificationError(AuthManagerError):
    """Исключение, возникающее при ошибке валидации JWT."""
    pass
