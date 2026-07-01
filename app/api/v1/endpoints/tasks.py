from typing import List, Optional
from fastapi import Query, HTTPException, status, APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.tasks import TaskResponse, TaskStatus, TaskPriority, TaskCreate, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter(
    tags=["tasks"],
)


@router.get("/tasks", response_model=List[TaskResponse])
async def print_tasks(
    task_status: Optional[TaskStatus] = Query(None, description="Фильтр по статусу"),
    project_id: Optional[int] = Query(None, description="Фильтр по проекту"),
    priority: Optional[TaskPriority] = Query(None, description="Фильтр по приоритету"),
    assignee_id: Optional[int] = Query(None, description="Фильтр по исполнителю"),
    limit: int = Query(100, ge=1, description="Лимит записей"),
    offset: int = Query(0, ge=0, description="Смещение"),
    db: AsyncSession = Depends(get_db)
):
    """
    Вывод задач с различными параметрами.
    :param task_status: Фильтрация по статусу задачи
    :param project_id: Фильтрация по проекту, в котором находятся задачи
    :param priority: Фильтрация по приоритету
    :param assignee_id: Фильтрация по исполнителю
    :param limit: Пагинация - определение количества выводимых задач
    :param offset: Пагинация - определение сдвига задач
    :param db: Сессия подключения к БД
    :return: Список задач
    """
    filters = {}
    if status:
        filters["status"] = status.value
    if project_id:
        filters["project_id"] = project_id
    if priority:
        filters["priority"] = priority.value
    if assignee_id:
        filters["assignee_id"] = assignee_id

    service = TaskService(db)
    return await service.get_all_tasks(filters, limit, offset)


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(data: TaskCreate,
                      db: AsyncSession = Depends(get_db)):
    """
    Создаёт в базе новую задачу.
    :param data: Данные для новой задачи
    :param db: Сессия подключения к БД
    :return: Новосозданная задача
    """
    service = TaskService(db)
    return await service.create_task(data.model_dump())


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def print_task(task_id: int,
                     db: AsyncSession = Depends(get_db)):
    """
    Выводит одну задачу с соответствующим ID.
    :param task_id: ID задачи
    :param db: Сессия подключения к БД
    :return: Задача
    """
    service = TaskService(db)
    return await service.get_task_by_id(task_id)


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int,
                      update_data: TaskUpdate,
                      db: AsyncSession = Depends(get_db)):
    """
    Обновляет задачу по её ID.
    Принимает только те поля, которые нужно изменить.

    :param task_id: ID задачи
    :param update_data: Изменённые данные
    :param db: Сессия подключения к БД
    :return: Изменённая задача
    """
    service = TaskService(db)
    return await service.update_task(task_id, update_data.model_dump(exclude_unset=True))


@router.delete("/tasks/{task_id}", response_model=TaskResponse)
async def delete_task(task_id: int,
                      db: AsyncSession = Depends(get_db)):
    """
    Удаление задачи с соответствующим ID.
    :param task_id: ID задачи
    :param db: Сессия подключения к БД
    :return: Удалённая задача
    """
    service = TaskService(db)
    return await service.delete_task(task_id)