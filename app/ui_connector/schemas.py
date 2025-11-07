"""
Pydantic-схемы (DTO) для модуля UI Connector.

Этот файл определяет структуры данных, которые `ui_connector` будет использовать
для отправки ответов на фронтенд. Эти схемы специально разработаны
и агрегированы для удобства UI-компонентов, чтобы минимизировать
логику обработки данных на стороне клиента.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict

# Базовые схемы, импортированные для композиции
# Предполагается, что эти схемы уже определены в других модулях
# и мы их здесь переиспользуем или адаптируем.
# Для примера, возьмем их из app/schemas/
from app.schemas.account import Account
from app.schemas.payment import Transaction
from app.schemas.product import FinancialGoal


class DashboardData(BaseModel):
    """
    Агрегированные данные для главной страницы (Dashboard).
    """
    net_worth: float = Field(..., description="Общий капитал пользователя")
    accounts: List[Account] = Field(..., description="Список счетов пользователя")
    spending_chart_data: Dict[str, float] = Field(..., description="Данные для круговой диаграммы трат по категориям")
    recent_transactions: List[Transaction] = Field(..., description="Список последних транзакций")
    financial_goals: List[FinancialGoal] = Field(..., description="Список финансовых целей")


class RecommendedCardOffer(BaseModel):
    """
    Схема для рекомендованной карты на странице "Карты".
    """
    # Эта схема может быть сложнее и включать в себя детали предложения
    # и причину рекомендации. Для начала сделаем ее простой.
    card_name: str
    bank_name: str
    potential_saving: float
    top_category_name: str
    benefits: List[str]


class CardsPageData(BaseModel):
    """
    Данные для страницы "Карты".
    """
    cards: List[Account] = Field(..., description="Список всех карт (дебетовых и кредитных)")
    recommendation: Optional[RecommendedCardOffer] = Field(None, description="Персональная рекомендация по новой карте")


class AssistantResponse(BaseModel):
    """
    Ответ от финансового ассистента.
    """
    text: str = Field(..., description="Текстовый ответ от AI-ассистента")


# Добавим схемы для "умных" сервисов по мере их реализации.
# Например:
class SmartDebitingCalculation(BaseModel):
    """
    Результат расчета для "Умного списания".
    """
    sufficient: bool
    shortfall: Optional[float] = None
    plan: Optional[List[Dict]] = None # План может иметь более строгую типизацию

