from typing import List
from fastapi import HTTPException, status, APIRouter

from app.schemas.projects import ProjectResponse, ProjectCreate, ProjectUpdate
from app.api.v1.endpoints.users import users_db


router = APIRouter(
    tags=["projects"],
)

projects_db = []

@router.get("/projects", response_model=List[ProjectResponse])
async def print_projects():
    """
    Вывод всех проектов
    """
    return projects_db


@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(data: ProjectCreate):
    """
    Создание нового проекта.
    Проверка на существование пользователя по ID.
    :param data: Данные по новому проекту
    :return: Новый проект
    """
    new_project = None
    for user in users_db:
        if user.get("id") == data.owner_id:
            new_project = data.dict()
            break

    if not new_project:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким ID не найден",
        )

    projects_db.append(new_project)
    return new_project


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def print_project(project_id: int):
    """
    Выводит один проект с соответствующим ID.
    :param project_id: ID проекта
    :return: Сам проект
    """
    project = None
    for p in projects_db:
        if p.get("project_id") == project_id:
            project = p
            break

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден"
        )
    return project


@router.patch("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: int, update_data: ProjectUpdate):
    """
    Обновляет проект по его ID.
    Принимает только те поля, которые нужно изменить.

    :param project_id: ID проекта
    :param update_data: Изменённые данные
    :return: Изменённый проект
    """
    project = None
    for p in projects_db:
        if p.get("project_id") == project_id:
            project = p
            break

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена"
        )

    # Преобразуем входные данные в словарь, исключая None-поля
    update_dict = update_data.dict(exclude_unset=True)

    for key, value in update_dict.items():
        if value is not None:
            project[key] = value

    return project


@router.delete("/projects/{project_id}", response_model=ProjectResponse)
async def delete_project(project_id: int):
    """
    Удаление проекта с соответствующим ID.
    :param project_id: ID проекта
    :return: Удалённый проект
    """
    project = None
    for p in projects_db:
        if p.get("project_id") == project_id:
            project = p
            break

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена"
        )
    projects_db.remove(project)
    return project