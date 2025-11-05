"""
Модуль для выполнения операций CRUD (Create, Read, Update, Delete) с токенами в базе данных.
Использует SQLAlchemy для взаимодействия с базой данных и Fernet для шифрования/дешифрования токенов.
"""
from sqlalchemy.orm import Session

from app.db import models
from app.security import encryption


def save_token(db: Session, bank_name: str, token: str, expires_in: int):
    """
    Сохраняет или обновляет токен доступа для указанного банка в базе данных.
    Токен шифруется перед сохранением.

    - `db`: Сессия базы данных SQLAlchemy.
    - `bank_name`: Название банка (например, 'vbank').
    - `token`: Токен доступа, полученный от банка.
    - `expires_in`: Время жизни токена в секундах.

    Если токен для данного банка уже существует, он обновляется; в противном случае создается новая запись.
    """
    encrypted_token = encryption.encrypt(token)
    db_token = db.query(models.Token).filter(models.Token.bank_name == bank_name).first()

    if db_token:
        # Обновляем существующий токен
        db_token.encrypted_token = encrypted_token
        db_token.expires_in = expires_in
    else:
        # Вставляем новый токен
        db_token = models.Token(
            bank_name=bank_name,
            encrypted_token=encrypted_token,
            expires_in=expires_in
        )
        db.add(db_token)

    db.commit()
    db.refresh(db_token)
    return db_token


def get_decrypted_token(db: Session, bank_name: str) -> str | None:
    """
    Получает зашифрованный токен для указанного банка из базы данных и дешифрует его.

    - `db`: Сессия базы данных SQLAlchemy.
    - `bank_name`: Название банка.

    Возвращает дешифрованный токен в виде строки или `None`, если токен не найден.
    """
    db_token = db.query(models.Token).filter(models.Token.bank_name == bank_name).first()
    if db_token:
        return encryption.decrypt(db_token.encrypted_token)
    return None
