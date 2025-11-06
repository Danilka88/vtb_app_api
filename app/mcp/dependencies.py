from sqlalchemy.orm import Session
from fastapi import Depends
from app.db.database import get_db
from app.mcp.services import MCPService

def get_mcp_service(db: Session = Depends(get_db)) -> MCPService:
    """
    Зависимость FastAPI для получения экземпляра MCPService.
    """
    return MCPService(db=db)
