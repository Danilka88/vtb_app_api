from fastapi import APIRouter

from app.api.v1.endpoints import auth, data, payments

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(data.router, prefix="/data", tags=["data"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
