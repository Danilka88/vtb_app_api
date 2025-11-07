"""
Сервис-оркестратор для модуля UI Connector.

Этот сервис является "мозгом" BFF-слоя. Он принимает запросы от роутера,
обращается к другим внутренним сервисам (таким как MCP, LLM),
агрегирует их ответы, выполняет необходимую бизнес-логику и
возвращает данные в формате, удобном для UI.
"""
from fastapi import Depends, HTTPException
from typing import Dict, List
import asyncio

# Импортируем сервисы, которые будет использовать наш оркестратор
from app.mcp.services import MCPService, get_mcp_service
# from app.llm_integration.services import LLMAgentService, get_llm_agent_service # Закомментировано до реализации

# Импортируем схемы данных для ответов
from . import schemas
from app.schemas.account import Account
from app.schemas.payment import Transaction


class UIService:
    """
    Сервис-оркестратор, который готовит данные для UI.
    """
    def __init__(
        self,
        mcp_service: MCPService = Depends(get_mcp_service),
        # llm_service: LLMAgentService = Depends(get_llm_agent_service) # Закомментировано до реализации
    ):
        self.mcp_service = mcp_service
        # self.llm_service = llm_service

    async def get_dashboard_data(self, user_id: str, consent_id: str) -> schemas.DashboardData:
        """
        Собирает, агрегирует и форматирует все данные для главной страницы.
        """
        # 1. Получаем счета через MCP-сервис
        # Для демонстрации используем жестко закодированные названия банков.
        # В реальном приложении это может быть список банков, к которым у пользователя есть доступ.
        bank_names = ["VBank", "ABank", "SBank"]
        mcp_account_responses = await self.mcp_service.get_all_accounts(
            bank_names=bank_names, user_id=user_id, consent_id=consent_id
        )

        accounts: List[Account] = []
        for response in mcp_account_responses:
            if response.status == "success" and response.data:
                # MCPService.get_all_accounts возвращает List[BankOperationResponse]
                # где data - это List[Account]
                accounts.extend([Account(**acc) for acc in response.data])
            elif response.status == "failed":
                print(f"Failed to fetch accounts from {response.bank_name}: {response.message}")

        # 2. Получаем транзакции для каждого счета
        all_transactions: List[Transaction] = []
        transaction_tasks = []
        for account in accounts:
            # Предполагаем, что get_transactions_for_account возвращает List[Transaction]
            transaction_tasks.append(
                self.mcp_service.get_transactions_for_account(
                    bank_name=account.bank_name,
                    user_id=user_id,
                    consent_id=consent_id,
                    account_id=account.account_id
                )
            )
        
        # Выполняем все запросы на транзакции параллельно
        transactions_results = await asyncio.gather(*transaction_tasks)

        for result in transactions_results:
            # MCPService.get_transactions_for_account возвращает List[Transaction] напрямую
            # или пустой список, если заглушка.
            all_transactions.extend([Transaction(**t) for t in result])

        # Сортируем транзакции по дате (от новых к старым)
        all_transactions.sort(key=lambda t: t.date, reverse=True)
        recent_transactions = all_transactions[:5] # Берем 5 последних

        # 3. Вычисляем общий капитал
        net_worth = sum(acc.balance for acc in accounts)

        # 4. Формируем данные для диаграммы трат
        spending_chart_data: Dict[str, float] = {}
        for t in all_transactions:
            if t.type == 'expense' and t.category != 'Переводы':
                category = t.category
                amount = abs(t.amount)
                spending_chart_data[category] = spending_chart_data.get(category, 0) + amount

        # 5. Получаем финансовые цели (пока заглушка)
        financial_goals = [] # Заглушка

        # 6. Собираем все в единую DTO
        dashboard_data = schemas.DashboardData(
            net_worth=net_worth,
            accounts=accounts,
            spending_chart_data=spending_chart_data,
            recent_transactions=recent_transactions,
            financial_goals=financial_goals,
        )

        return dashboard_data

# Зависимость для получения сервиса в роутере
def get_ui_service(service: UIService = Depends(UIService)) -> UIService:
    return service
