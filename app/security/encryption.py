from cryptography.fernet import Fernet

from app.core.config import settings

# Initialize Fernet with the key from settings
# The key must be 32 bytes and URL-safe base64 encoded.
# You can generate a key using: from cryptography.fernet import Fernet; Fernet.generate_key()
fernet = Fernet(settings.ENCRYPTION_KEY.encode())

def encrypt(data: str) -> bytes:
    """Encrypts a string and returns bytes."""
    return fernet.encrypt(data.encode())

def decrypt(encrypted_data: bytes) -> str:
    """Decrypts bytes and returns a string."""
    return fernet.decrypt(encrypted_data).decode()
