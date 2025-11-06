from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.mcp.schemas import MultiBankAccountsRequest, BankOperationResponse, MultiBankConsentRequest
from app.mcp.dependencies import get_mcp_service
from app.mcp.services import MCPService

router = APIRouter()

@router.post("/accounts/all", response_model=List[BankOperationResponse])
async def get_accounts_from_multiple_banks(
    request: MultiBankAccountsRequest,
    mcp_service: MCPService = Depends(get_mcp_service)
):
    """
    Получает счета из нескольких банков для заданного пользователя.
    """
    results = await mcp_service.get_all_accounts(request.bank_names, request.user_id)
    return results

@router.post("/consents/create", response_model=BankOperationResponse)
async def create_consent_via_mcp(
    request: MultiBankConsentRequest,
    mcp_service: MCPService = Depends(get_mcp_service)
):
    """
    Создает согласие для указанного банка через MCP.
    """
    result = await mcp_service.create_bank_consent(
        request.bank_name,
        request.permissions,
        request.user_id,
        request.debtor_account,
        request.amount,
        request.currency
    )
    return result

# TODO: Добавить другие эндпоинты для мультибанковых операций (платежи, продукты и т.д.)
