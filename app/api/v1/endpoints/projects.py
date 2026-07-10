from typing import List
from fastapi import status, APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_db
from app.schemas.projects import ProjectResponse, ProjectCreate, ProjectUpdate
from app.services.project_service import ProjectService


router = APIRouter(
    tags=["projects"],
)


@router.get("/projects", response_model=List[ProjectResponse])
async def print_projects(
        db: AsyncSession = Depends(get_db),
        current_user: dict = Depends(get_current_user),
):
    """ Вывод всех проектов. """
    project_service = ProjectService(db)
    return await project_service.get_all_projects(current_user)


@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
        data: ProjectCreate,
        db: AsyncSession = Depends(get_db),
        current_user: dict = Depends(get_current_user),
):
    """
    Создание нового проекта.
    Проверка на существование пользователя по ID.
    """
    project_service = ProjectService(db)
    return await project_service.create_project(data.model_dump(), current_user)


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def print_project(
        project_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: dict = Depends(get_current_user),
):
    """ Выводит один проект с соответствующим ID. """
    project_service = ProjectService(db)
    return await project_service.get_by_id(project_id, current_user)


@router.patch("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
        project_id: int,
        update_data: ProjectUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: dict = Depends(get_current_user),
):
    """
    Обновляет проект по его ID.
    Принимает только те поля, которые нужно изменить.
    """
    project_service = ProjectService(db)
    return await project_service.update_project(project_id, update_data.model_dump(exclude_unset=True), current_user)


@router.delete("/projects/{project_id}", response_model=ProjectResponse)
async def delete_project(
        project_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: dict = Depends(get_current_user),
):
    """ Удаление проекта с соответствующим ID. """
    project_service = ProjectService(db)
    return await project_service.delete_project(project_id, current_user)