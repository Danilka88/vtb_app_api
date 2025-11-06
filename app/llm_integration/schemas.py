from pydantic import BaseModel, Field
from typing import List, Optional, Any

class AgentQueryRequest(BaseModel):
    """
    Модель запроса пользователя к ИИ-агенту.
    """
    user_id: str = Field(..., description="Идентификатор пользователя")
    query: str = Field(..., description="Запрос пользователя на естественном языке")

class ToolCall(BaseModel):
    """
    Модель для описания вызова инструмента агентом.
    """
    tool_name: str = Field(..., description="Название инструмента, который будет вызван")
    args: dict = Field(..., description="Аргументы для вызова инструмента")

class ToolOutput(BaseModel):
    """
    Модель для описания вывода инструмента.
    """
    tool_name: str = Field(..., description="Название вызванного инструмента")
    output: Any = Field(..., description="Вывод инструмента")

class AgentResponse(BaseModel):
    """
    Модель ответа от ИИ-агента.
    """
    response: str = Field(..., description="Ответ агента на естественном языке")
    tool_calls: Optional[List[ToolCall]] = Field(None, description="Список вызовов инструментов, если агент решил их использовать")
    tool_outputs: Optional[List[ToolOutput]] = Field(None, description="Список выводов инструментов, если они были вызваны")
    raw_response: Optional[Any] = Field(None, description="Сырой ответ от LLM (для отладки)")
