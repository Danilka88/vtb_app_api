"""
Модуль для шифрования и дешифрования данных с использованием Fernet из библиотеки cryptography.
Используется для безопасного хранения конфиденциальной информации, такой как токены доступа.
"""
from cryptography.fernet import Fernet

from app.core.config import settings

# Инициализируем Fernet с ключом из настроек.
# Ключ должен быть 32 байта и закодирован в base64, безопасном для URL.
# Его можно сгенерировать с помощью: from cryptography.fernet import Fernet; Fernet.generate_key()
fernet = Fernet(settings.ENCRYPTION_KEY.encode())

def encrypt(data: str) -> bytes:
    """
    Шифрует строку данных.

    - `data`: Строка для шифрования.

    Возвращает зашифрованные данные в виде байтов.
    """
    return fernet.encrypt(data.encode())

def decrypt(encrypted_data: bytes) -> str:
    """
    Дешифрует байты данных.

    - `encrypted_data`: Зашифрованные данные в виде байтов.

    Возвращает дешифрованную строку.
    """
    return fernet.decrypt(encrypted_data).decode()
