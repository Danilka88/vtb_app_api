"""
API-роутер для агрегации данных из различных источников.

Этот роутер действует как основная точка входа для фронтенда,
используя `ui_connector` сервис для сбора и подготовки данных.
"""
from fastapi import APIRouter, Depends, Body
from pydantic import BaseModel
from typing import Any

from app.ui_connector.services import UIService, get_ui_service
from app.ui_connector.schemas import FinancialData

router = APIRouter()

class AggregatorRequest(BaseModel):
    user_id: str
    # В будущем здесь можно будет передавать список consent_id или другие параметры
    # для более гранулярного запроса данных.

@router.post(
    "/all",
    response_model=FinancialData,
    summary="Получить все агрегированные финансовые данные",
    description="Возвращает единый объект `FinancialData` со всей информацией, необходимой для рендеринга UI, агрегируя данные из всех подключенных банков и сервисов.",
)
async def get_all_aggregated_data(
    # request_data: AggregatorRequest, # Пока user_id не используется в заглушке, можно закомментировать
    ui_service: UIService = Depends(get_ui_service),
) -> Any:
    """
    Основной эндпоинт для фронтенда.
    
    Собирает, агрегирует и форматирует все данные, необходимые для работы UI,
    включая счета, транзакции, цели, подписки, кредиты, рекомендации и т.д.
    """
    # user_id = request_data.user_id
    # В данный момент сервис-заглушка не требует user_id, но в будущем он будет использоваться.
    aggregated_data = await ui_service.get_aggregated_financial_data()
    return aggregated_data
