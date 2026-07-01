from typing import List
from fastapi import status, APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.projects import ProjectResponse, ProjectCreate, ProjectUpdate
from app.services.project_service import ProjectService


router = APIRouter(
    tags=["projects"],
)


@router.get("/projects", response_model=List[ProjectResponse])
async def print_projects(db: AsyncSession = Depends(get_db)):
    """
    Вывод всех проектов
    """
    project_service = ProjectService(db)
    return await project_service.get_all_projects()


@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(data: ProjectCreate,
                         db: AsyncSession = Depends(get_db)):
    """
    Создание нового проекта.
    Проверка на существование пользователя по ID.
    :param data: Данные по новому проекту
    :param db: Сессия подключения к БД
    :return: Новый проект
    """
    project_service = ProjectService(db)
    return await project_service.create_project(data.model_dump())


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def print_project(project_id: int,
                        db: AsyncSession = Depends(get_db)):
    """
    Выводит один проект с соответствующим ID.
    :param project_id: ID проекта
    :param db: Сессия подключения к БД
    :return: Сам проект
    """
    project_service = ProjectService(db)
    return await project_service.get_by_id(project_id)


@router.patch("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: int,
                         update_data: ProjectUpdate,
                         db: AsyncSession = Depends(get_db)):
    """
    Обновляет проект по его ID.
    Принимает только те поля, которые нужно изменить.

    :param project_id: ID проекта
    :param update_data: Изменённые данные
    :param db: Сессия подключения к БД
    :return: Изменённый проект
    """
    project_service = ProjectService(db)
    return await project_service.update_project(project_id, update_data.dict(exclude_unset=True))


@router.delete("/projects/{project_id}", response_model=ProjectResponse)
async def delete_project(project_id: int,
                         db: AsyncSession = Depends(get_db)):
    """
    Удаление проекта с соответствующим ID.
    :param project_id: ID проекта
    :param db: Сессия подключения к БД
    :return: Удалённый проект
    """
    project_service = ProjectService(db)
    return await project_service.delete_project(project_id)