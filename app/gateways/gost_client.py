"""
Модуль, реализующий клиент для взаимодействия с API ГОСТ (например, для CIBA аутентификации).
"""
import asyncio
import httpx

from app.banks.base_client import BaseBankClient
from app.security.jwt_utils import create_signed_ciba_jwt


class GostClient(BaseBankClient):
    """
    Клиент для взаимодействия с API, использующим стандарты ГОСТ, например, для CIBA аутентификации.
    Наследуется от `BaseBankClient` для использования общих настроек клиента.
    """
    async def initiate_ciba_authentication(self, login_hint: str, binding_message: str) -> dict:
        """
        Инициирует аутентификацию по отдельному каналу (CIBA).
        Формирует и подписывает JWT-запрос, отправляет его на эндпоинт `/bc-authorize`.

        - `login_hint`: Идентификатор пользователя.
        - `binding_message`: Сообщение для связывания сессии.

        Возвращает `auth_req_id` и `expires_in`.
        """
        signed_jwt = create_signed_ciba_jwt(login_hint, binding_message, self.api_url)
        response = await self.client.post(
            f"{self.api_url}/bc-authorize",
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data={
                "client_id": self.client_id,
                "request": signed_jwt
            }
        )
        response.raise_for_status()
        return response.json()

    async def poll_for_tokens(self, auth_req_id: str) -> dict:
        """
        Периодически опрашивает эндпоинт `/token` для получения токенов после CIBA аутентификации.
        Продолжает опрос, пока пользователь не подтвердит аутентификацию или не истечет время.

        - `auth_req_id`: Идентификатор запроса аутентификации, полученный на этапе инициации CIBA.

        Возвращает `access_token`, `id_token`, `refresh_token`.
        """
        while True:
            response = await self.client.post(
                f"{self.api_url}/token",
                data={
                    "grant_type": "urn:openid:params:grant-type:ciba",
                    "auth_req_id": auth_req_id,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret  # Для аутентификации клиента
                }
            )
            try:
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 400:
                    error_data = e.response.json()
                    if error_data.get("error") == "authorization_pending":
                        await asyncio.sleep(5)  # Опрашиваем каждые 5 секунд
                        continue
                    elif error_data.get("error") == "slow_down":
                        await asyncio.sleep(error_data.get("interval", 5)) # Используем интервал, если предоставлен
                        continue
                raise  # Перевыбрасываем другие HTTP ошибки
