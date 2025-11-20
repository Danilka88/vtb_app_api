"""
Pydantic-схемы (DTO) для модуля UI Connector.

Этот файл определяет структуры данных, которые `ui_connector` будет использовать
для отправки ответов на фронтенд. Эти схемы точно соответствуют интерфейсам
TypeScript из `ui/types.ts`, чтобы обеспечить полную совместимость
между бэкендом и фронтендом.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Literal

# --- Базовые модели, соответствующие ui/types.ts ---

class Account(BaseModel):
    id: str
    name: str
    bank_name: str = Field(..., alias="bankName")
    last4: str
    balance: float
    type: Literal['debit', 'credit', 'savings']
    brand_color: str = Field(..., alias="brandColor")

class Transaction(BaseModel):
    id: str
    date: str
    description: str
    amount: float
    type: Literal['income', 'expense']
    category: str

class FinancialGoal(BaseModel):
    id: str
    name: str
    current_amount: float = Field(..., alias="currentAmount")
    target_amount: float = Field(..., alias="targetAmount")

class NightSafeData(BaseModel):
    enabled: bool
    included_account_ids: List[str] = Field(..., alias="includedAccountIds")
    target_account_id: str = Field(..., alias="targetAccountId")
    stats: Dict[str, float]

class SmartPayData(BaseModel):
    enabled: bool
    included_account_ids: List[str] = Field(..., alias="includedAccountIds")

class CashbackCategory(BaseModel):
    bank_name: str = Field(..., alias="bankName")
    categories: Dict[str, int]

class SpecialOffer(BaseModel):
    id: str
    partner_name: str = Field(..., alias="partnerName")
    bank_name: str = Field(..., alias="bankName")
    description: str
    expiry_date: str = Field(..., alias="expiryDate")
    brand_color: str = Field(..., alias="brandColor")

class ExchangeRate(BaseModel):
    bank_name: str = Field(..., alias="bankName")
    from_currency: Literal['RUB'] = Field(..., alias="from")
    to_currency: Literal['USD', 'EUR', 'CNY'] = Field(..., alias="to")
    buy: float
    sell: float
    promotion: Optional[str] = None

class Subscription(BaseModel):
    id: str
    name: str
    amount: float
    billing_cycle: Literal['monthly', 'yearly'] = Field(..., alias="billingCycle")
    next_payment_date: str = Field(..., alias="nextPaymentDate")
    linked_account_id: str = Field(..., alias="linkedAccountId")
    status: Literal['active', 'blocked']

class Loan(BaseModel):
    id: str
    name: str
    bank_name: str = Field(..., alias="bankName")
    remaining_amount: float = Field(..., alias="remainingAmount")
    interest_rate: float = Field(..., alias="interestRate")
    monthly_payment: float = Field(..., alias="monthlyPayment")
    next_payment_date: str = Field(..., alias="nextPaymentDate")
    linked_account_id: str = Field(..., alias="linkedAccountId")

class RefinancingOffer(BaseModel):
    id: str
    bank_name: str = Field(..., alias="bankName")
    new_interest_rate: float = Field(..., alias="newInterestRate")
    description: str
    max_amount: int = Field(..., alias="maxAmount")
    brand_color: str = Field(..., alias="brandColor")

class MarketplaceSubscription(BaseModel):
    id: str
    name: str
    logo_url: str = Field(..., alias="logoUrl")
    cost: float
    billing_cycle: Literal['monthly', 'yearly'] = Field(..., alias="billingCycle")
    benefits: List[str]
    related_merchants: List[str] = Field(..., alias="relatedMerchants")
    cashback_category: str = Field(..., alias="cashbackCategory")

class TrustIssue(BaseModel):
    id: str
    bank_name: str = Field(..., alias="bankName")
    account_id: Optional[str] = Field(None, alias="accountId")
    type: str
    severity: Literal['high', 'medium', 'low']
    title: str
    description: str
    recommendation: str

class RecommendedCardOffer(BaseModel):
    id: str
    name: str
    bank_name: str = Field(..., alias="bankName")
    brand_color: str = Field(..., alias="brandColor")
    benefits: List[str]
    is_credit: bool = Field(..., alias="isCredit")
    cashback_rates: Dict[str, int] = Field(..., alias="cashbackRates")

class BudgetEnvelope(BaseModel):
    id: str
    name: str
    type: Literal['essentials', 'wants', 'savings']
    allocated_amount: float = Field(..., alias="allocatedAmount")
    spent_amount: float = Field(..., alias="spentAmount")
    forecasted_amount: float = Field(..., alias="forecastedAmount")
    color: str

class BudgetPlan(BaseModel):
    total_monthly_income: int = Field(..., alias="totalMonthlyIncome")
    safe_daily_spend: int = Field(..., alias="safeDailySpend")
    days_remaining_in_month: int = Field(..., alias="daysRemainingInMonth")
    envelopes: List[BudgetEnvelope]
    insights: List[str]

class HealthComponent(BaseModel):
    id: str
    category: Literal['spending', 'debt', 'savings', 'regularity']
    label: str
    score: int
    max_score: int = Field(..., alias="maxScore")
    status: Literal['excellent', 'good', 'fair', 'poor']
    advice: str

class Badge(BaseModel):
    id: str
    name: str
    description: str
    icon_name: str = Field(..., alias="iconName")
    unlocked: bool

class Reward(BaseModel):
    id: str
    title: str
    description: str
    required_score: int = Field(..., alias="requiredScore")
    is_locked: bool = Field(..., alias="isLocked")

class FinancialHealth(BaseModel):
    total_score: int = Field(..., alias="totalScore")
    components: List[HealthComponent]
    badges: List[Badge]
    rewards: List[Reward]


# --- Главная агрегирующая модель ---

class FinancialData(BaseModel):
    """
    Агрегированный объект, содержащий все финансовые данные для пользователя.
    Полностью соответствует `FinancialData` в `ui/types.ts`.
    """
    net_worth: float = Field(..., alias="netWorth")
    accounts: List[Account]
    transactions: List[Transaction]
    goals: List[FinancialGoal]
    night_safe: NightSafeData = Field(..., alias="nightSafe")
    smart_pay: SmartPayData = Field(..., alias="smartPay")
    cashback_categories: List[CashbackCategory] = Field(..., alias="cashbackCategories")
    special_offers: List[SpecialOffer] = Field(..., alias="specialOffers")
    exchange_rates: List[ExchangeRate] = Field(..., alias="exchangeRates")
    subscriptions: List[Subscription]
    loans: List[Loan]
    refinancing_offers: List[RefinancingOffer] = Field(..., alias="refinancingOffers")
    marketplace_subscriptions: List[MarketplaceSubscription] = Field(..., alias="marketplaceSubscriptions")
    recommended_card_offers: List[RecommendedCardOffer] = Field(..., alias="recommendedCardOffers")
    trust_issues: List[TrustIssue] = Field(..., alias="trustIssues")
    budget_plan: BudgetPlan = Field(..., alias="budgetPlan")
    financial_health: FinancialHealth = Field(..., alias="financialHealth")