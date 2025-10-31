from fastapi import FastAPI

from app.db.database import Base, engine
from app.api.v1 import api_router

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "Hello from vtb-app-api!"}
