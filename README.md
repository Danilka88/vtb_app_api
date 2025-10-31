# Интеллектуальный Мультибанковский Финансовый Советник (ИМФС)

Это бэкенд-сервис для проекта ИМФС, разработанный на FastAPI.

## Настройка и запуск

### 1. Установка зависимостей

Для установки всех необходимых зависимостей, выполните команду:

```bash
uv pip sync pyproject.toml
```

### 2. Настройка переменных окружения

Создайте файл `.env` в корне проекта. Вы можете скопировать `.env.example` (если он есть) или создать файл вручную со следующими переменными:

```
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
ENCRYPTION_KEY=your_32_byte_long_encryption_key
DATABASE_URL=sqlite:///./app.db
```

- `CLIENT_ID` и `CLIENT_SECRET`: Ваши учетные данные, полученные от организаторов хакатона.
- `ENCRYPTION_KEY`: 32-байтный ключ для шифрования токенов. Вы можете сгенерировать новый ключ, выполнив в терминале:
  ```bash
  python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
  ```
- `DATABASE_URL`: URL для подключения к базе данных. По умолчанию используется SQLite.

### 3. Запуск приложения

Для запуска сервера в режиме разработки с автоматической перезагрузкой выполните:

```bash
uvicorn main:app --reload
```

Сервер будет доступен по адресу `http://127.0.0.1:8000`.

## Доступные API эндпоинты

### Аутентификация и авторизация

- **`POST /api/v1/auth/init-bank-tokens`**
  - **Описание:** Инициирует процесс получения и сохранения банковских токенов для всех поддерживаемых банков (`vbank`, `abank`, `sbank`).
  - **Ответ:**
    ```json
    {
      "message": "Bank tokens initialized successfully."
    }
    ```

- **`POST /api/v1/auth/create-consent`**
  - **Описание:** Создает согласие для доступа к данным пользователя.
  - **Тело запроса:**
    ```json
    {
      "bank_name": "vbank",
      "user_id": "team042-1"
    }
    ```
  - **Ответ:**
    ```json
    {
      "message": "Consent created successfully.",
      "consent_id": "consent-xxxxxxxxxxxx"
    }
    ```

### Получение данных

- **`POST /api/v1/data/accounts`**
  - **Описание:** Получает список счетов пользователя.
  - **Тело запроса:**
    ```json
    {
      "bank_name": "vbank",
      "consent_id": "consent-xxxxxxxxxxxx",
      "user_id": "team042-1"
    }
    ```

- **`POST /api/v1/data/accounts/{account_id}/balances`**
  - **Описание:** Получает балансы для конкретного счета.
  - **Тело запроса:**
    ```json
    {
      "bank_name": "vbank",
      "consent_id": "consent-xxxxxxxxxxxx",
      "user_id": "team042-1"
    }
    ```

- **`POST /api/v1/data/accounts/{account_id}/transactions`**
  - **Описание:** Получает транзакции для конкретного счета.
  - **Тело запроса:**
    ```json
    {
      "bank_name": "vbank",
      "consent_id": "consent-xxxxxxxxxxxx",
      "user_id": "team042-1"
    }
    ```

## Важно: Учетные данные

- `CLIENT_ID`: `team042` (код вашей команды).
- `CLIENT_SECRET`: Секретный ключ, полученный от организаторов хакатона (например, `QlXkpyJlRATlGD25xYp7azqIA5Cx4qcc`).
