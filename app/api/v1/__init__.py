from fastapi import APIRouter

from app.api.v1.endpoints import auth, data, payments, products, aggregator
from app.mcp.router import router as mcp_router
from app.llm_integration.router import router as llm_router
from app.public_ai_adapter.router import router as public_ai_adapter_router
from app.ui_connector.router import router as ui_connector_router

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(data.router, prefix="/data", tags=["data"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(aggregator.router, prefix="/aggregator", tags=["aggregator"])
api_router.include_router(mcp_router, prefix="/mcp", tags=["mcp"])
api_router.include_router(llm_router, prefix="/llm", tags=["llm"])
api_router.include_router(public_ai_adapter_router, prefix="/public_adapter", tags=["public_adapter"])
api_router.include_router(ui_connector_router, prefix="/ui", tags=["ui_connector"])
