from fastapi import APIRouter, Depends
from app.api.v1.endpoints import projects, users, tasks, attachments
from app.core.security import get_current_user


public_router = APIRouter(
    prefix="/api/v1"
)
public_router.include_router(users.public_router)

protected_router = APIRouter(
    prefix="/api/v1",
    tags=["api_v1"],
    dependencies=[Depends(get_current_user)]
)
protected_router.include_router(projects.router)
protected_router.include_router(users.protected_router)
protected_router.include_router(tasks.router)
protected_router.include_router(attachments.router)