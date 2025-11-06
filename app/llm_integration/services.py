from langchain_ollama import OllamaLLM
from langchain_classic.agents.agent import AgentExecutor
from langchain_classic.agents.react.agent import create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from typing import List, Any

from app.llm_integration.tools import get_all_accounts_from_mcp # Импортируем наши инструменты
from app.llm_integration.schemas import AgentResponse, ToolCall, ToolOutput

class LLMAgentService:
    def __init__(self, model_name: str = "gemma3:4b"):
        self.llm = OllamaLLM(model=model_name)
        self.tools = [
            get_all_accounts_from_mcp,
            # TODO: Добавить другие инструменты здесь
        ]
        self.agent_executor = self._initialize_agent()

    def _initialize_agent(self) -> AgentExecutor:
        # Определяем шаблон промпта для агента
        # Этот шаблон должен быть достаточно подробным, чтобы агент понимал свою роль, доступные инструменты и формат ответа.
        prompt_template = PromptTemplate.from_template("""
        Ты - финансовый ассистент, который помогает пользователям управлять своими финансами, используя мультибанковскую платформу.
        У тебя есть доступ к следующим инструментам:

        {tools}

        Используй формат ReAct для взаимодействия:
        Вопрос: пользовательский запрос
        Мысль: тебе нужно подумать, что делать
        Действие: название_инструмента[аргументы]
        Наблюдение: результат действия
        ... (повторяется Мысль/Действие/Наблюдение N раз)
        Мысль: я знаю окончательный ответ
        Финальный Ответ: окончательный ответ на пользовательский запрос

        Начни!

        Action: the action to take, should be one of [{tool_names}]
        Вопрос: {input}
        {agent_scratchpad}
        """)

        # Создаем агента
        agent = create_react_agent(self.llm, self.tools, prompt_template)

        # Создаем исполнителя агента
        agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True, handle_parsing_errors=True)
        return agent_executor

    async def process_user_query(self, user_id: str, query: str) -> AgentResponse:
        # Здесь мы будем передавать user_id в инструменты, если это необходимо.
        # Для этого можно обернуть вызов агента или модифицировать инструменты.
        # Пока что, для простоты, user_id будет передаваться напрямую в инструменты.

        # TODO: Реализовать более сложную логику для обработки tool_calls и tool_outputs
        # Сейчас агент просто возвращает финальный ответ.

        response = await self.agent_executor.invoke({"input": query, "user_id": user_id})
        
        # В зависимости от того, как агент возвращает свой ответ (например, если он включает tool_calls), 
        # мы можем разобрать его и вернуть в соответствующем формате.
        # Для начала, просто вернем финальный ответ.
        return AgentResponse(response=response["output"], raw_response=response)
