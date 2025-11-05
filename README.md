# Интеллектуальный Мультибанковский Финансовый Советник (ИМФС)

Это бэкенд-сервис для проекта ИМФС, разработанный на FastAPI. Он агрегирует финансовые данные из нескольких банков, анализирует их и предоставляет персональные финансовые советы.

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
VBANK_API_URL=https://vbank.example.com/api/v1
ABANK_API_URL=https://abank.example.com/api/v1
SBANK_API_URL=https://sbank.example.com/api/v1
```

- `CLIENT_ID` и `CLIENT_SECRET`: Ваши учетные данные, полученные от организаторов хакатона.
- `ENCRYPTION_KEY`: 32-байтный ключ для шифрования токенов. Вы можете сгенерировать новый ключ, выполнив в терминале:
  ```bash
  python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
  ```
- `DATABASE_URL`: URL для подключения к базе данных. По умолчанию используется SQLite.
- `VBANK_API_URL`, `ABANK_API_URL`, `SBANK_API_URL`: Базовые URL для API соответствующих банков.

### 3. Запуск приложения

Для запуска сервера в режиме разработки с автоматической перезагрузкой выполните:

```bash
uvicorn main:app --reload
```

Сервер будет доступен по адресу `http://127.0.0.1:8000`.

## Консольные команды

### Запуск тестов

Для запуска всех тестов проекта выполните:

```bash
PYTHONPATH=/Users/danil_ka88/Desktop/vrb_api/vtb_app_api pytest -q /Users/danil_ka88/Desktop/vrb_api/vtb_app_api/tests/test_vbank_payments_api.py
```
Или, если вы хотите запустить все тесты в директории `tests`:
```bash
PYTHONPATH=/Users/danil_ka88/Desktop/vrb_api/vtb_app_api pytest -q tests/
```
Флаг `-q` делает вывод более кратким.

### Генерация ключа шифрования

Для генерации 32-байтного ключа шифрования (для переменной `ENCRYPTION_KEY` в `.env`):

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## Доступные API эндпоинты

### Аутентификация и управление согласиями

- **`POST /api/v1/auth/init-bank-tokens`**
  - **Описание:** Инициирует процесс получения и сохранения банк-токенов для всех поддерживаемых банков (`vbank`, `abank`, `sbank`). Эти токены необходимы для дальнейшего взаимодействия с API банков (например, для создания согласий).
  - **Ответ:**
    ```json
    {
      "message": "Токены банков успешно инициализированы."
    }
    ```

- **`POST /api/v1/auth/create-consent`**
  - **Описание:** Создает согласие для доступа к данным пользователя или для выполнения платежа.
    - Для согласия на доступ к данным: укажите `bank_name`, `user_id` и `permissions` (например, `["ReadAccountsDetail", "ReadBalances"]`).
    - Для платежного согласия: дополнительно укажите `debtor_account` (ID счета списания) и `amount` (сумму). В `permissions` должен быть `CreateDomesticSinglePayment`.
  - **Тело запроса (пример для доступа к данным):**
    ```json
    {
      "bank_name": "vbank",
      "user_id": "team042-1",
      "permissions": ["ReadAccountsDetail", "ReadBalances"]
    }
    ```
  - **Тело запроса (пример для платежного согласия):**
    ```json
    {
      "bank_name": "vbank",
      "user_id": "team042-1",
      "permissions": ["CreateDomesticSinglePayment"],
      "debtor_account": "acc-12345",
      "amount": "100.00"
    }
    ```
  - **Ответ:**
    ```json
    {
      "message": "Согласие успешно создано.",
      "consent_id": "consent-xxxxxxxxxxxx"
    }
    ```

- **`GET /api/v1/auth/consents/{consent_id}`**
  - **Описание:** Получает детали существующего согласия по его ID.
  - **Параметры запроса:**
    - `bank_name`: Название банка (например, `vbank`).
    - `user_id`: Идентификатор пользователя (например, `team042-1`).
  - **Ответ:**
    ```json
    {
      "message": "Детали согласия успешно получены.",
      "details": {
        "data": {
          "consentId": "consent-xxxxxxxxxxxx",
          "status": "Authorized",
          "permissions": ["ReadAccountsDetail", "ReadBalances"],
          // ... другие детали согласия
        }
      }
    }
    ```

- **`DELETE /api/v1/auth/consents/{consent_id}`**
  - **Описание:** Отзывает (удаляет) согласие по его ID.
  - **Параметры запроса:**
    - `bank_name`: Название банка (например, `vbank`).
    - `user_id`: Идентификатор пользователя (например, `team042-1`).
  - **Ответ:**
    ```json
    {
      "message": "Согласие успешно отозвано.",
      "details": {
        "status": "success",
        "message": "Consent revoked successfully (no content)"
      }
    }
    ```

### Получение данных

- **`POST /api/v1/data/accounts`**
  - **Описание:** Получает список счетов пользователя для указанного банка, используя предоставленный `consent_id`. `consent_id` должен быть предварительно получен с разрешениями на чтение счетов (например, `ReadAccountsDetail`).
  - **Тело запроса:**
    ```json
    {
      "bank_name": "vbank",
      "consent_id": "consent-xxxxxxxxxxxx",
      "user_id": "team042-1"
    }
    ```
  - **Ответ:**
    ```json
    {
      "message": "Счета успешно получены.",
      "accounts": [
        {
          "accountId": "acc-1511",
          "status": "Enabled",
          // ... другие детали счета
        }
      ]
    }
    ```

- **`POST /api/v1/data/accounts/{account_id}/balances`**
  - **Описание:** Получает балансы для конкретного счета (`account_id`) в заданном банке, используя предоставленный `consent_id`. `consent_id` должен быть предварительно получен с разрешениями на чтение балансов (например, `ReadBalances`).
  - **Тело запроса:**
    ```json
    {
      "bank_name": "vbank",
      "consent_id": "consent-xxxxxxxxxxxx",
      "user_id": "team042-1"
    }
    ```
  - **Ответ:**
    ```json
    {
      "message": "Балансы успешно получены.",
      "balances": {
        // ... детали баланса
      }
    }
    ```

- **`POST /api/v1/data/accounts/{account_id}/transactions`**
  - **Описание:** Получает историю транзакций для конкретного счета (`account_id`) в заданном банке, используя предоставленный `consent_id`. `consent_id` должен быть предварительно получен с разрешениями на чтение транзакций (например, `ReadTransactionsDetail`).
  - **Тело запроса:**
    ```json
    {
      "bank_name": "vbank",
      "consent_id": "consent-xxxxxxxxxxxx",
      "user_id": "team042-1"
    }
    ```
  - **Ответ:**
    ```json
    {
      "message": "Транзакции успешно получены.",
      "transactions": [
        {
          // ... детали транзакции
        }
      ]
    }
    ```

## Важно: Учетные данные и тестовые пользователи

- `CLIENT_ID`: `team042` (код вашей команды).
- `CLIENT_SECRET`: Секретный ключ, полученный от организаторов хакатона (например, `QlXkpyJlRATlGD25xYp7azqIA5Cx4qcc`).
- **Тестовые пользователи:** Для тестирования используйте `user_id` в формате `team042-X`, где `X` - число от 1 до 10 (например, `team042-1`, `team042-2`).