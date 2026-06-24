from fastapi import FastAPI

from app.api.v1.router import main_router

app = FastAPI(
    title="TaskFlow API",
    description="TaskFlow API - это приложение для управления задачами, пользователями, проектами и многим другим.",
    version="1.0",
)

app.include_router(main_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}

