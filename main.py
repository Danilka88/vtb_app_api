from fastapi import FastAPI

from app.db.database import Base, engine
from app.api.v1.endpoints import auth

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])


@app.get("/")
async def root():
    return {"message": "Hello from vtb-app-api!"}
