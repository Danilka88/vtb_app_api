from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Intellectual Multi-Bank Financial Advisor"
    CLIENT_ID: str
    CLIENT_SECRET: str
    ENCRYPTION_KEY: str
    DATABASE_URL: str

    VBANK_API_URL: str = "https://vbank.open.bankingapi.ru"
    ABANK_API_URL: str = "https://abank.open.bankingapi.ru"
    SBANK_API_URL: str = "https://sbank.open.bankingapi.ru"

    class Config:
        env_file = ".env"


settings = Settings()
