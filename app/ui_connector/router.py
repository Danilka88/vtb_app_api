"""
API-роутер для модуля UI Connector.

Определяет все эндпоинты, которые предоставляет Backend for Frontend (BFF).
Каждый эндпоинт соответствует определенному компоненту или странице в UI,
предоставляя ему все необходимые, уже агрегированные и обработанные данные.
"""
from fastapi import APIRouter, Depends, Body
from pydantic import BaseModel

from .services import UIService, get_ui_service
from . import schemas

router = APIRouter()

# --- Модели для тел запросов ---
class DashboardRequest(BaseModel):
    user_id: str
    consent_id: str

# --- Эндпоинты ---

@router.post(
    "/dashboard",
    response_model=schemas.DashboardData,
    summary="Получить агрегированные данные для главной страницы",
    description="Возвращает единый объект со всей информацией, необходимой для рендеринга Dashboard в UI.",
)
async def get_dashboard_data(
    request_data: DashboardRequest,
    ui_service: UIService = Depends(get_ui_service),
):
    """
    Эндпоинт для главной страницы.
    
    - **user_id**: Идентификатор пользователя.
    - **consent_id**: Идентификатор согласия на доступ к данным.
    """
    dashboard_data = await ui_service.get_dashboard_data(
        user_id=request_data.user_id,
        consent_id=request_data.consent_id
    )
    return dashboard_data

# Здесь будут добавлены другие эндпоинты для UI:
# - /cards
# - /assistant
# - /smart-debiting/calculate
# - и т.д.
