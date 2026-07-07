from fastapi import APIRouter
from app.api.v1.endpoints import projects, users, tasks, attachments


main_router = APIRouter(
    prefix="/api/v1",
    tags=["api_v1"],
)

main_router.include_router(projects.router)
main_router.include_router(users.router)
main_router.include_router(tasks.router)
main_router.include_router(attachments.router)