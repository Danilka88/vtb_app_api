from abc import ABC
import httpx

class BaseService(ABC):
    """
    Абстрактный базовый класс для всех сервисов, взаимодействующих с API банка.
    Предоставляет общий доступ к HTTP-клиенту, базовому URL API и основному клиенту банка.
    """
    def __init__(self, client):
        # 'client' должен быть экземпляром BaseBankClient или его наследника.
        # Это обеспечивает доступ к общему httpx.AsyncClient, URL API и конфигурации.
        self._client = client

    @property
    def client(self) -> httpx.AsyncClient:
        """
        Возвращает асинхронный HTTP-клиент, используемый основным клиентом банка.
        """
        # Предполагаем, что у основного клиента есть атрибут _async_client
        return self._client._async_client

    @property
    def api_url(self) -> str:
        """
        Возвращает базовый URL API банка, к которому относится сервис.
        """
        return self._client.api_url

    @property
    def main_client(self):
        """
        Возвращает экземпляр основного клиента банка (например, VBankClient).
        """
        return self._client
