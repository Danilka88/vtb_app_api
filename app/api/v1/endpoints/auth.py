from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db import crud
from app.db.database import SessionLocal
from app.banks.vbank_client import VBankClient

router = APIRouter()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/init-tokens")
async def init_tokens(db: Session = Depends(get_db)):
    """
    Initializes and saves bank tokens for all supported banks.
    """
    # VBank
    vbank_client = VBankClient(
        client_id=settings.CLIENT_ID,
        client_secret=settings.CLIENT_SECRET,
        api_url=settings.VBANK_API_URL
    )
    vbank_token_data = await vbank_client.get_bank_token()
    crud.save_token(
        db=db,
        bank_name="vbank",
        token=vbank_token_data["access_token"],
        expires_in=vbank_token_data["expires_in"]
    )

    # ABank (to be implemented)

    # SBank (to be implemented)

    return {"message": "Tokens initialized successfully."}
