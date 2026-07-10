from typing import List, Optional
from fastapi import Query, HTTPException, status, APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_db
from app.repositories.user_repository import UserRepository
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
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Вывод задач с различными параметрами фильтрации и пагинации.

    ---
    **Фильтры:**
    - `task_status` – статус задачи (enum)
    - `project_id` – ID проекта
    - `priority` – приоритет (enum)
    - `assignee_id` – ID исполнителя

    **Пагинация:**
    - `limit` – максимальное количество записей (по умолчанию 100)
    - `offset` – смещение для пропуска записей (по умолчанию 0)
    """
    filters = {}
    if task_status:
        filters["status"] = task_status.value
    if project_id:
        filters["project_id"] = project_id
    if priority:
        filters["priority"] = priority.value
    if assignee_id:
        filters["assignee_id"] = assignee_id

    service = TaskService(db)
    return await service.get_all_tasks(filters, limit, offset, current_user)


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
        data: TaskCreate,
        db: AsyncSession = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    """
    Создаёт в базе новую задачу.

    ---
    **Приоритеты:**
    - Выполняется
    - Запланирована
    - Завершена
    - Брошена

    **Приоритеты:**
    - Низкий
    - Средний
    - Высокий
    """
    # Поиск пользователя в БД
    username =  current_user.get("preferred_username")
    user_repo = UserRepository(db)
    user = await user_repo.get_by_username(username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    # Подготовка данных
    task_data = data.model_dump()
    task_data["user_id"] = user.id

    service = TaskService(db)
    return await service.create_task(task_data, current_user)


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def print_task(
        task_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: dict = Depends(get_current_user),
):
    """ Выводит одну задачу с соответствующим ID. """
    service = TaskService(db)
    return await service.get_task_by_id(task_id, current_user)


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
        task_id: int,
        update_data: TaskUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: dict = Depends(get_current_user),
):
    """
    Обновляет задачу по её ID.
    Принимает только те поля, которые нужно изменить.

    ---
    **Приоритеты:**
    - Выполняется
    - Запланирована
    - Завершена
    - Брошена

    **Приоритеты:**
    - Низкий
    - Средний
    - Высокий
    """
    service = TaskService(db)
    return await service.update_task(task_id, update_data.model_dump(exclude_unset=True), current_user)


@router.delete("/tasks/{task_id}", response_model=TaskResponse)
async def delete_task(
        task_id: int,
        db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """ Удаление задачи с соответствующим ID. """
    service = TaskService(db)
    return await service.delete_task(task_id, current_user)