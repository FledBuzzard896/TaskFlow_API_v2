from fastapi import FastAPI, Depends

from app.api.v1.router import public_router, protected_router

app = FastAPI(
    title="TaskFlow API",
    description="TaskFlow API - это приложение для управления задачами, пользователями, проектами и многим другим.",
    version="1.0",
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": False,
        "clientId": "taskflow-api",
        "realm": "taskflow",
        "appName": "TaskFlow API",
    },
)


app.include_router(public_router)
app.include_router(protected_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}

