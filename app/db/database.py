"""
Модуль для настройки подключения к базе данных с использованием SQLAlchemy.
Определяет движок базы данных, фабрику сессий и базовый класс для декларативных моделей.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
# Фабрика сессий для создания объектов сессий базы данных.
# autocommit=False и autoflush=False гарантируют, что изменения не будут автоматически сохраняться.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для декларативных моделей SQLAlchemy.
Base = declarative_base()
