from fastapi import APIRouter, Depends, HTTPException
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


@router.post("/init-bank-tokens")
async def init_bank_tokens(db: Session = Depends(get_db)):
    """
    Initializes and saves bank tokens for all supported banks using the simple bank-token flow.
    """
    # VBank
    vbank_client = VBankClient(
        client_id=settings.CLIENT_ID,
        client_secret=settings.CLIENT_SECRET,
        api_url=settings.VBANK_API_URL
    )
    try:
        vbank_token_data = await vbank_client.get_bank_token()
        crud.save_token(
            db=db,
            bank_name="vbank",
            token=vbank_token_data["access_token"],
            expires_in=vbank_token_data["expires_in"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get token for VBank: {e}")

    # ABank (to be implemented)

    # SBank (to be implemented)

    return {"message": "Bank tokens initialized successfully."}
