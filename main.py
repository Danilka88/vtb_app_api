from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.db.database import Base, engine
from app.api.v1 import api_router

app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Событие запуска
    Base.metadata.create_all(bind=engine)
    print("База данных инициализирована.")
    yield
    # Событие завершения (если нужно)
    print("Приложение завершает работу.")

app = FastAPI(lifespan=lifespan)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "Hello from vtb-app-api!"}
