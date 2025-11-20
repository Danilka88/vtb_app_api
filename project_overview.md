# Обзор Архитектуры Проекта: Интеллектуальный Мультибанковский Финансовый Советник (ИМФС)

Этот документ представляет высокоуровневую схему архитектуры ИМФС, разработанную для демонстрации ключевых компонентов, их взаимодействия и основных преимуществ системы. Схема создана таким образом, чтобы быть понятной как техническим специалистам, так и тем, кто впервые знакомится с проектом.

```mermaid
C4Context
    title Интеллектуальный Мультибанковский Финансовый Советник (ИМФС) - Обзор Системы

    Person(user, "Пользователь", "Вы управляете своими финансами.")
    System(ui_app, "Веб-приложение (UI)", "Интуитивно понятный интерфейс (React/TS).")
    System_Ext(bank_apis, "API Банков", "VBank, ABank, SBank - данные ваших счетов.")
    System_Ext(ollama, "Ollama", "Локальная LLM (gemma3:4b) для ИИ-агентов.")
    System_Ext(external_llm, "Внешние LLM", "Claude, OpenAI - для расширенной аналитики (опционально).")

    Rel(user, ui_app, "Управляет финансами через")

    Boundary(backend_system, "Backend ИМФС (FastAPI / Python) - Ядро интеллекта и агрегации") {

        System_Ext(ui_connector, "UI Connector (BFF)", "API, оптимизированное для UI. Одно окно для всех данных.")
        System(mcp_service, "MCP Service", "Унификация работы с банками. Один стандарт для всех API.")
        System(auth_manager, "Auth Manager", "Безопасная аутентификация. Токены и кэширование.")
        System(bank_clients, "Банковские Клиенты", "Гибкость: легко добавить новый банк.")
        System(llm_integration, "LLM Интеграция", "ИИ-агенты анализируют данные и дают советы.")
        System(public_ai_adapter, "Public AI Adapter", "Безопасный мост для внешних ИИ.")
        System(database, "База Данных", "Хранение данных и состояний (PostgreSQL/SQLite).")

        Rel(ui_app, ui_connector, "Получает все UI-данные за 1 запрос", "HTTP/REST")

        Rel(ui_connector, mcp_service, "Запрашивает агрегированные данные")
        Rel(ui_connector, llm_integration, "Обращается к ИИ-ассистенту")

        Rel(mcp_service, auth_manager, "Запрашивает токены доступа к банкам")
        Rel(mcp_service, bank_clients, "Вызывает специфичные для банка операции", "Полиморфный доступ")

        Rel(llm_integration, mcp_service, "Использует функции MCP как инструменты ИИ-агентов")
        Rel(llm_integration, ollama, "Анализирует запросы и формирует ответы")
        Rel(llm_integration, public_ai_adapter, "Предоставляет API для внешних ИИ")

        Rel(auth_manager, database, "Сохраняет/читает зашифрованные токены")
        Rel(bank_clients, auth_manager, "Использует токены для запросов")
    }

    Rel(bank_clients, bank_apis, "Взаимодействует", "OpenBanking API")
    Rel(public_ai_adapter, external_llm, "Принимает запросы", "Tool Use / Function Calling")

    UpdateElementStyle(user, $fontColor='#ffffff', $bgColor='#0D9488')
    UpdateElementStyle(ui_app, $fontColor='#ffffff', $bgColor='#4F46E5')
    UpdateElementStyle(bank_apis, $fontColor='#ffffff', $bgColor='#B91C1C')
    UpdateElementStyle(ollama, $fontColor='#ffffff', $bgColor='#0F766E')
    UpdateElementStyle(external_llm, $fontColor='#ffffff', $bgColor='#6D28D9')

    UpdateElementStyle(ui_connector, $fontColor='#ffffff', $bgColor='#10B981')
    UpdateElementStyle(mcp_service, $fontColor='#ffffff', $bgColor='#EAB308')
    UpdateElementStyle(auth_manager, $fontColor='#ffffff', $bgColor='#DB2777')
    UpdateElementStyle(bank_clients, $fontColor='#ffffff', $bgColor='#3B82F6')
    UpdateElementStyle(llm_integration, $fontColor='#ffffff', $bgColor='#8B5CF6')
    UpdateElementStyle(public_ai_adapter, $fontColor='#ffffff', $bgColor='#F472B6')
    UpdateElementStyle(database, $fontColor='#ffffff', $bgColor='#64748B')

    UpdateBoundaryStyle(backend_system, $borderColor='#FCD34D', $borderStyle='Dashed')
```

### Пояснения к схеме:

*   **Пользователь:** Взаимодействует с системой через удобный веб-интерфейс.
*   **Веб-приложение (UI):** Фронтенд на React/TypeScript, который предоставляет все функциональные возможности для пользователя.
*   **UI Connector (BFF):** Специализированный API-шлюз для фронтенда. Он агрегирует данные из разных частей бэкенда, чтобы UI мог получать все необходимое за один оптимизированный запрос. **Преимущество: Упрощает разработку UI, повышает производительность и безопасность.**
*   **MCP Service (Multi-Bank Communication Protocol):** Сердце мультибанковской функциональности. Он абстрагирует и унифицирует взаимодействие со всеми банковскими API, предоставляя единый интерфейс. **Преимущество: Легкое добавление новых банков, снижение сложности.**
*   **Auth Manager:** Централизованный модуль для управления аутентификацией и авторизацией. Отвечает за получение, обновление и безопасное хранение токенов доступа к банкам. **Преимущество: Единая точка управления безопасностью, кэширование токенов для скорости.**
*   **Банковские Клиенты:** Набор полиморфных реализаций клиентов для каждого конкретного банка (VBank, ABank, SBank). Каждый клиент знает, как общаться со "своим" банком. **Преимущество: Гибкость и расширяемость для интеграции с новыми банками.**
*   **LLM Интеграция:** Модуль, отвечающий за работу ИИ-агентов. Использует LangChain для создания агентов, которые могут анализировать данные и давать советы. **Преимущество: Мощные ИИ-возможности, адаптация к разным LLM.**
*   **Public AI Adapter:** Безопасный адаптер, который позволяет внешним ИИ-платформам (например, Claude, OpenAI) безопасно взаимодействовать с функциями нашего бэкенда. **Преимущество: Открытость для интеграции с передовыми ИИ, не раскрывая внутреннюю архитектуру.**
*   **База Данных:** Хранит важную информацию, включая зашифрованные токены доступа и пользовательские настройки.
*   **API Банков:** Внешние системы, предоставляющие финансовые данные через OpenBanking API.
*   **Ollama/Внешние LLM:** Модели большого языка, используемые для обработки запросов ИИ-агентами. Ollama может работать локально, внешние LLM — через облачные сервисы.

Эта схема демонстрирует, как ИМФС объединяет различные модули и внешние системы для создания мощного, безопасного и интеллектуального финансового инструмента.
