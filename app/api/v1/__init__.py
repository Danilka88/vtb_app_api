from fastapi import APIRouter

from app.api.v1.endpoints import auth, data, payments, products
from app.mcp.router import router as mcp_router

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(data.router, prefix="/data", tags=["data"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(mcp_router, prefix="/mcp", tags=["mcp"])
