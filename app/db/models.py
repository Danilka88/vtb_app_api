"""
Модуль, определяющий модели SQLAlchemy для базы данных.
Содержит модель `Token` для хранения зашифрованных токенов доступа банков.
"""
from sqlalchemy import Column, Integer, String, LargeBinary

from app.db.database import Base


class Token(Base):
    """
    Модель базы данных для хранения токенов доступа банков.
    Токены хранятся в зашифрованном виде.
    """
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True) # Уникальный идентификатор записи токена
    bank_name = Column(String, unique=True, index=True) # Название банка (уникальное)
    encrypted_token = Column(LargeBinary, nullable=False) # Зашифрованный токен доступа
    expires_in = Column(Integer, nullable=False) # Время жизни токена в секундах
