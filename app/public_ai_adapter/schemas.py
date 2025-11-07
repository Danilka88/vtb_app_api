from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal

class ToolCall(BaseModel):
    """
    Модель, описывающая один вызов инструмента, как его представляет внешняя ИИ-модель.
    """
    id: str = Field(..., description="Уникальный идентификатор вызова, генерируемый моделью.")
    function: Dict[str, Any] = Field(..., description="Функция, которую нужно вызвать. Содержит имя и аргументы.")
    type: Literal["function"] = "function"

class ToolCallRequest(BaseModel):
    """
    Модель запроса, который адаптер ожидает от внешней системы.
    """
    user_id: str = Field(..., description="Идентификатор конечного пользователя, для которого выполняется операция.")
    tool_calls: List[ToolCall] = Field(..., description="Список инструментов, которые нужно вызвать.")

class ToolOutput(BaseModel):
    """
    Модель для ответа с результатом одного вызова инструмента.
    """
    tool_call_id: str = Field(..., description="Идентификатор вызова, на который дается ответ.")
    output: str = Field(..., description="Результат выполнения инструмента в виде строки.")

class ToolCallResponse(BaseModel):
    """
    Модель ответа, который адаптер отправляет обратно внешней системе.
    """
    tool_outputs: List[ToolOutput]
