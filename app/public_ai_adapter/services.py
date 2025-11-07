import json
from typing import List, Dict, Any

from app.mcp.services import MCPService
from app.public_ai_adapter.schemas import ToolCall, ToolOutput

class PublicAIAdapterService:
    """
    Сервис для трансляции вызовов инструментов от внешних ИИ-моделей
    во внутренние вызовы MCPService.
    """
    def __init__(self, mcp_service: MCPService):
        self.mcp_service = mcp_service
        # Реестр доступных инструментов. Ключ - имя, как его видит внешняя модель.
        # Значение - соответствующий метод MCPService.
        self.tool_registry = {
            "get_all_accounts": self.mcp_service.get_all_accounts,
            "create_bank_consent": self.mcp_service.create_bank_consent,
            # TODO: Добавить сюда другие методы MCP по мере их появления
        }

    async def execute_tool_calls(self, user_id: str, tool_calls: List[ToolCall]) -> List[ToolOutput]:
        """
        Выполняет список вызовов инструментов и возвращает их результаты.
        """
        outputs: List[ToolOutput] = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.get("name")
            
            # Аргументы приходят в виде JSON-строки, их нужно распарсить
            try:
                arguments_str = tool_call.function.get("arguments", "{}")
                arguments = json.loads(arguments_str)
            except json.JSONDecodeError:
                output_content = f"Error: Invalid JSON in arguments: {arguments_str}"
                outputs.append(ToolOutput(tool_call_id=tool_call.id, output=output_content))
                continue

            # Добавляем user_id в аргументы, так как он нужен для большинства вызовов
            arguments["user_id"] = user_id

            if tool_name in self.tool_registry:
                try:
                    method_to_call = self.tool_registry[tool_name]
                    
                    # Отделяем 'user_id' и 'consent_id', так как они передаются в сервис отдельно
                    user_id_from_args = arguments.pop("user_id", user_id)
                    consent_id_from_args = arguments.pop("consent_id", None)

                    # Вызываем метод, передавая остальные аргументы как kwargs
                    result = await method_to_call(user_id=user_id_from_args, consent_id=consent_id_from_args, **arguments)
                    
                    # Сериализуем результат в JSON-строку для вывода
                    output_content = json.dumps(result.model_dump(exclude_none=True), ensure_ascii=False, indent=2) if not isinstance(result, list) else json.dumps([res.model_dump(exclude_none=True) for res in result], ensure_ascii=False, indent=2)

                except Exception as e:
                    output_content = f"Error executing tool '{tool_name}': {str(e)}"
            else:
                output_content = f"Error: Tool '{tool_name}' not found."

            outputs.append(ToolOutput(tool_call_id=tool_call.id, output=output_content))
        
        return outputs
