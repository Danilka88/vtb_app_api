from sqlalchemy.orm import Session

from app.db import models
from app.security import encryption


def save_token(db: Session, bank_name: str, token: str, expires_in: int):
    encrypted_token = encryption.encrypt(token)
    db_token = db.query(models.Token).filter(models.Token.bank_name == bank_name).first()

    if db_token:
        # Update existing token
        db_token.encrypted_token = encrypted_token
        db_token.expires_in = expires_in
    else:
        # Insert new token
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
    db_token = db.query(models.Token).filter(models.Token.bank_name == bank_name).first()
    if db_token:
        return encryption.decrypt(db_token.encrypted_token)
    return None
