from sqlalchemy import Column, Integer, String, LargeBinary

from app.db.database import Base


class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    bank_name = Column(String, unique=True, index=True)
    encrypted_token = Column(LargeBinary, nullable=False)
    expires_in = Column(Integer, nullable=False)
