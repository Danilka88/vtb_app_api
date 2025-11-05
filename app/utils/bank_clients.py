import httpx
from fastapi import HTTPException

from app.core.config import settings
from app.banks.vbank_client import VBankClient
from app.banks.abank_client import ABankClient
from app.banks.sbank_client import SBankClient


def get_bank_client(bank_name: str):
    """
    Вспомогательная функция для получения экземпляра клиента банка по его имени.
    """
    if bank_name == "vbank":
        return VBankClient(client_id=settings.CLIENT_ID, client_secret=settings.CLIENT_SECRET, api_url=settings.VBANK_API_URL)
    elif bank_name == "abank":
        return ABankClient(client_id=settings.CLIENT_ID, client_secret=settings.CLIENT_SECRET, api_url=settings.ABANK_API_URL)
    elif bank_name == "sbank":
        return SBankClient(client_id=settings.CLIENT_ID, client_secret=settings.CLIENT_SECRET, api_url=settings.SBANK_API_URL)
    else:
        raise HTTPException(status_code=400, detail="Неподдерживаемый банк.")
