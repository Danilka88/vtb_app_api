"""
Сервис-оркестратор для модуля UI Connector.

Этот сервис является "мозгом" BFF-слоя. Он принимает запросы от роутера,
обращается к другим внутренним сервисам (таким как MCP, LLM),
агрегирует их ответы, выполняет необходимую бизнес-логику и
возвращает данные в формате, удобном для UI.

В текущей реализации сервис использует моковые данные для имитации
полноценного ответа, что позволяет фронтенду разрабатываться и тестироваться
независимо от полной реализации всех внутренних сервисов.
"""
from fastapi import Depends
from typing import Any
from datetime import datetime, timedelta, timezone

from app.mcp.services import MCPService, get_mcp_service
from . import schemas

class UIService:
    def __init__(
        self,
        mcp_service: MCPService = Depends(get_mcp_service),
    ):
        self.mcp_service = mcp_service

    async def get_aggregated_financial_data(self) -> schemas.FinancialData:
        """
        Собирает, агрегирует и форматирует все данные для UI.

        ВНИМАНИЕ: В данный момент метод возвращает статичные моковые данные,
        аналогичные тем, что используются в `ui/services/financialService.ts`.
        Это сделано для ускорения разработки и тестирования UI.
        В будущем здесь будет реализована логика сбора реальных данных
        через `MCPService`.
        """
        
        # --- Начало блока моковых данных ---
        
        accounts_data = [
            {'id': 'acc_tbank_debit', 'name': 'ABank Black', 'bankName': 'ABank', 'last4': '1111', 'balance': 28340.70, 'type': 'debit', 'brandColor': '#EF3124'},
            {'id': 'acc_sber_debit', 'name': 'SBank Карта', 'bankName': 'SBank', 'last4': '2222', 'balance': 41200.90, 'type': 'debit', 'brandColor': '#228B22'},
            {'id': 'acc_alfa_debit', 'name': 'A-Карта', 'bankName': 'ABank', 'last4': '7777', 'balance': 15800.00, 'type': 'debit', 'brandColor': '#EF3124'},
            {'id': 'acc_tbank_credit', 'name': 'Fly Airlines', 'bankName': 'ABank', 'last4': '3333', 'balance': -25000.00, 'type': 'credit', 'brandColor': '#00BFFF'},
            {'id': 'acc_vtb_savings', 'name': 'Сейф', 'bankName': 'VBank', 'last4': '4444', 'balance': 540100.00, 'type': 'savings', 'brandColor': '#0033A0'},
            {'id': 'acc_sber_savings', 'name': 'Накопительный', 'bankName': 'SBank', 'last4': '5555', 'balance': 210000.00, 'type': 'savings', 'brandColor': '#005522'},
        ]
        
        transactions_data = [
            {'id': 't1', 'date': (datetime.now() - timedelta(days=1)).isoformat(), 'description': 'Зарплата', 'amount': 120000, 'type': 'income', 'category': 'Зарплата'},
            {'id': 't2', 'date': (datetime.now() - timedelta(days=2)).isoformat(), 'description': 'Perekrestok', 'amount': -3450.50, 'type': 'expense', 'category': 'Супермаркеты'},
            {'id': 't3', 'date': (datetime.now() - timedelta(days=2)).isoformat(), 'description': 'Yandex.Go', 'amount': -450.00, 'type': 'expense', 'category': 'Такси'},
            {'id': 't4', 'date': (datetime.now() - timedelta(days=3)).isoformat(), 'description': 'Yandex.Plus', 'amount': -299.00, 'type': 'expense', 'category': 'Подписки'},
            {'id': 't5', 'date': (datetime.now() - timedelta(days=4)).isoformat(), 'description': 'Ресторан "Огонек"', 'amount': -5600.00, 'type': 'expense', 'category': 'Рестораны'},
        ]

        goals_data = [
            {'id': 'g1', 'name': 'Отпуск в Таиланде', 'currentAmount': 210000, 'targetAmount': 350000},
            {'id': 'g2', 'name': 'Новый ноутбук', 'currentAmount': 45000, 'targetAmount': 150000},
        ]
        
        mock_data = {
            "netWorth": sum(acc['balance'] for acc in accounts_data),
            "accounts": accounts_data,
            "transactions": transactions_data,
            "goals": goals_data,
            "nightSafe": {
                "enabled": True,
                "includedAccountIds": ['acc_tbank_debit', 'acc_sber_debit', 'acc_alfa_debit'],
                "targetAccountId": 'acc_vtb_savings',
                "stats": {"yesterday": 120.54, "month": 3450.12, "total": 15230.88},
            },
            "smartPay": {
                "enabled": True,
                "includedAccountIds": ['acc_tbank_debit', 'acc_sber_debit', 'acc_alfa_debit', 'acc_tbank_credit'],
            },
            "cashbackCategories": [
                {"bankName": 'ABank', "categories": {'Рестораны': 5, 'АЗС': 3, 'Путешествия': 2, 'Супермаркеты': 3, 'Подписки': 10, 'Книги': 5, 'Такси': 5}},
                {"bankName": 'SBank', "categories": {'Супермаркеты': 2, 'Рестораны': 1, 'АЗС': 1, 'Доставка': 5}},
            ],
            "specialOffers": [
                {'id': 'so1', 'partnerName': 'Ozon', 'bankName': 'ABank', 'description': 'Кэшбэк 10% на все покупки электроники в приложении Ozon', 'expiryDate': (datetime.now() + timedelta(days=15)).isoformat(), 'brandColor': '#4f46e5'},
                {'id': 'so2', 'partnerName': 'M.Video', 'bankName': 'SBank', 'description': 'Скидка 2000₽ при покупке от 20000₽ по SBank Карте', 'expiryDate': (datetime.now() + timedelta(days=10)).isoformat(), 'brandColor': '#ef4444'},
            ],
            "exchangeRates": [
                {'bankName': 'ABank', 'from': 'RUB', 'to': 'USD', 'buy': 90.5, 'sell': 92.8, 'promotion': 'Лучший курс в приложении'},
                {'bankName': 'SBank', 'from': 'RUB', 'to': 'USD', 'buy': 89.9, 'sell': 94.1},
                {'bankName': 'VBank', 'from': 'RUB', 'to': 'USD', 'buy': 90.1, 'sell': 93.5},
            ],
            "subscriptions": [
                {'id': 'sub1', 'name': 'Yandex.Plus', 'amount': 299, 'billingCycle': 'monthly', 'nextPaymentDate': (datetime.now() + timedelta(days=2)).isoformat(), 'linkedAccountId': 'acc_tbank_debit', 'status': 'active'},
                {'id': 'sub2', 'name': 'IVI', 'amount': 399, 'billingCycle': 'monthly', 'nextPaymentDate': datetime.now().isoformat(), 'linkedAccountId': 'acc_sber_debit', 'status': 'active'},
            ],
            "loans": [
                {'id': 'loan1', 'name': 'Автокредит', 'bankName': 'SBank', 'remainingAmount': 850000, 'interestRate': 8.5, 'monthlyPayment': 25000, 'nextPaymentDate': (datetime.now() + timedelta(days=12)).isoformat(), 'linkedAccountId': 'acc_sber_debit'},
                {'id': 'loan2', 'name': 'Ипотека', 'bankName': 'VBank', 'remainingAmount': 4500000, 'interestRate': 9.2, 'monthlyPayment': 42000, 'nextPaymentDate': (datetime.now() + timedelta(days=18)).isoformat(), 'linkedAccountId': 'acc_tbank_debit'},
            ],
            "refinancingOffers": [
                {'id': 'ref1', 'bankName': 'ABank', 'newInterestRate': 8.5, 'description': 'Лучшее предложение по рефинансированию ипотеки', 'maxAmount': 10000000, 'brandColor': '#EF3124'},
            ],
            "marketplaceSubscriptions": [
                 {'id': 'ms1', 'name': 'Яндекс Плюс', 'logoUrl': '', 'cost': 299, 'billingCycle': 'monthly', 'benefits': ['Кинопоиск', 'Яндекс.Музыка', 'Баллы Плюса'], 'relatedMerchants': ['Yandex.Go', 'KinoPoisk'], 'cashbackCategory': 'Подписки'},
            ],
            "recommendedCardOffers": [
                {'id': 'rec_card_1', 'name': 'ABank Premium', 'bankName': 'ABank', 'brandColor': '#333333', 'benefits': ['Повышенный кэшбэк в ресторанах'], 'isCredit': False, 'cashbackRates': {'Рестораны': 10}},
            ],
            "trustIssues": [
                {'id': 'ti1', 'bankName': 'SBank', 'accountId': 'acc_sber_savings', 'type': 'low_interest', 'severity': 'high', 'title': 'Низкая ставка по накопительному счету', 'description': 'Ваш счет в SBank имеет ставку 7%. В VBank ставка 12%.', 'recommendation': 'Переведите средства в VBank.'},
            ],
            "budgetPlan": {
                'totalMonthlyIncome': 240000, 'safeDailySpend': 3200, 'daysRemainingInMonth': 12,
                'envelopes': [
                    {'id': 'env1', 'name': 'Обязательные платежи', 'type': 'essentials', 'allocatedAmount': 120000, 'spentAmount': 95000, 'forecastedAmount': 118000, 'color': '#3b82f6'},
                    {'id': 'env2', 'name': 'Развлечения и Хотелки', 'type': 'wants', 'allocatedAmount': 72000, 'spentAmount': 55000, 'forecastedAmount': 75000, 'color': '#a855f7'},
                    {'id': 'env3', 'name': 'Накопления и Инвестиции', 'type': 'savings', 'allocatedAmount': 48000, 'spentAmount': 48000, 'forecastedAmount': 48000, 'color': '#22c55e'}
                ],
                'insights': ["Ваши расходы на 'Развлечения' превышают норму.","Вы отлично справляетесь с накоплениями!"]
            },
            "financialHealth": {
                'totalScore': 78,
                'components': [
                    {'id': 'comp_spending', 'category': 'spending', 'label': 'Контроль трат', 'score': 24, 'maxScore': 30, 'status': 'good', 'advice': 'Вы держитесь в рамках бюджета.'},
                    {'id': 'comp_debt', 'category': 'debt', 'label': 'Кредитная нагрузка', 'score': 20, 'maxScore': 30, 'status': 'fair', 'advice': 'Платежи по кредитам составляют 25% от дохода.'},
                ],
                'badges': [
                    {'id': 'b1', 'name': 'Зарплатник', 'description': 'Регулярные поступления', 'iconName': 'briefcase', 'unlocked': True},
                    {'id': 'b2', 'name': 'Сберегатель', 'description': 'Накопительный счет растет', 'iconName': 'piggy', 'unlocked': True},
                ],
                'rewards': [
                     {'id': 'r1', 'title': 'Повышенный кэшбэк', 'description': '+1% на все покупки', 'requiredScore': 70, 'isLocked': False},
                     {'id': 'r2', 'title': 'Скидка на кредит', 'description': '-0.5% к ставке', 'requiredScore': 85, 'isLocked': True},
                ]
            }
        }
        
        # --- Конец блока моковых данных ---
        
        # Валидируем и возвращаем данные в соответствии со схемой
        return schemas.FinancialData(**mock_data)

def get_ui_service(service: UIService = Depends(UIService)) -> UIService:
    return service