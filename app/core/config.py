from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Класс для управления настройками приложения, загружаемыми из переменных окружения.
    Использует Pydantic BaseSettings для валидации и загрузки конфигурации.
    """
    PROJECT_NAME: str = "Интеллектуальный Мультибанковский Финансовый Советник" # Название проекта
    CLIENT_ID: str # Идентификатор клиента для взаимодействия с API банков
    CLIENT_SECRET: str # Секрет клиента для взаимодействия с API банков
    ENCRYPTION_KEY: str # Ключ для шифрования конфиденциальных данных (например, токенов)
    DATABASE_URL: str # URL для подключения к базе данных (например, SQLite или PostgreSQL)

    VBANK_API_URL: str = "https://vbank.open.bankingapi.ru" # Базовый URL API VBank
    ABANK_API_URL: str = "https://abank.open.bankingapi.ru" # Базовый URL API ABank
    SBANK_API_URL: str = "https://sbank.open.bankingapi.ru" # Базовый URL API SBank

    CLIENT_CERT_PATH: str | None = None # Путь к файлу клиентского сертификата для mTLS
    CLIENT_KEY_PATH: str | None = None # Путь к файлу приватного ключа клиентского сертификата для mTLS

    class Config:
        env_file = ".env"


settings = Settings()
