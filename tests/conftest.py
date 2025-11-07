import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from app.db.database import Base, get_db
from app.auth_manager.services import BaseAuthManager
from app.auth_manager.dependencies import get_auth_manager
from main import app

# --- Mock Auth Manager ---

class MockAuthManager(BaseAuthManager):
    """
    Мок-реализация менеджера аутентификации для тестов.
    Возвращает предопределенный токен без реальных HTTP-запросов.
    """
    MOCK_TOKEN = "mock_access_token_for_tests"

    async def get_access_token(self, db: Session, bank_name: str) -> str:
        print(f"\nDEBUG: MockAuthManager.get_access_token called for bank: {bank_name}")
        return self.MOCK_TOKEN

    async def verify_jwt(self, token: str, bank_api_url: str) -> dict:
        # Для тестов, где не требуется валидация JWT, можно вернуть пустой dict
        return {"sub": "mock_user"}

# --- Database Fixtures ---

# Используем in-memory SQLite для тестов
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module", name="session")
def session_fixture():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

# --- Test Client Fixture ---

@pytest.fixture(scope="module", name="client")
def client_fixture(session: TestingSessionLocal):
    """
    Основная фикстура для тестов API.
    - Создает тестовый клиент FastAPI.
    - Переопределяет зависимость get_db для использования тестовой БД.
    - Переопределяет зависимость get_auth_manager для использования MockAuthManager.
    """
    def get_test_db():
        try:
            yield session
        finally:
            # Не закрываем сессию здесь, т.к. она управляется фикстурой 'session'
            pass

    def get_mock_auth_manager():
        return MockAuthManager()

    # Переопределяем зависимости
    app.dependency_overrides[get_db] = get_test_db
    app.dependency_overrides[get_auth_manager] = get_mock_auth_manager
    
    yield TestClient(app)
    
    # Очищаем переопределения после завершения тестов модуля
    app.dependency_overrides.clear()
