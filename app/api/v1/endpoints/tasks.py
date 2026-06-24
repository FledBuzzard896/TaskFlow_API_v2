from typing import List, Optional
from fastapi import Query, HTTPException, status, APIRouter

from app.api.v1.endpoints.projects import projects_db
from app.api.v1.endpoints.users import users_db
from app.schemas.tasks import TaskResponse, TaskStatus, TaskPriority, TaskCreate, TaskUpdate


router = APIRouter(
    tags=["tasks"],
)

tasks_db = []

@router.get("/tasks", response_model=List[TaskResponse])
async def print_tasks(
    task_status: Optional[TaskStatus] = Query(None, description="Фильтр по статусу"),
    project_id: Optional[int] = Query(None, description="Фильтр по проекту"),
    priority: Optional[TaskPriority] = Query(None, description="Фильтр по приоритету"),
    assignee_id: Optional[int] = Query(None, description="Фильтр по исполнителю"),
    limit: int = Query(100, ge=1, description="Лимит записей"),
    offset: int = Query(0, ge=0, description="Смещение"),
):
    """
    Вывод задач с различными параметрами.
    :param task_status: Фильтрация по статусу задачи
    :param project_id: Фильтрация по проекту, в котором находятся задачи
    :param priority: Фильтрация по приоритету
    :param assignee_id: Фильтрация по исполнителю
    :param limit: Пагинация - определение количества выводимых задач
    :param offset: Пагинация - определение сдвига задач
    :return: Список задач
    """
    filtered = tasks_db[:]

    # Фильтрация
    if task_status:
        filtered = [task for task in filtered if task.get("status") == task_status.value]
    if project_id:
        filtered = [task for task in filtered if task.get("project_id") == project_id]
    if priority:
        filtered = [task for task in filtered if task.get("priority") == priority.value]
    if assignee_id:
        filtered = [task for task in filtered if task.get("assignee_id") == assignee_id]

    #Пагинация
    filtered = filtered[offset:offset+limit]

    if not filtered:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задачи не найдены"
        )
    return filtered


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(data: TaskCreate):
    """
    Создаёт в базе новую задачу.
    :param data: Данные для новой задачи
    :return: Новосозданная задача
    """
    isAuthor = False
    isAssignee = False
    isProject = False

    for u in users_db:
        if data.get("user_id") == u["user_id"]:
            isAuthor = True
            break
        if data.get("assignee_id") == u["user_id"]:
            isAssignee = True
            break

    for p in projects_db:
        if data.get("project_id") == p["project_id"]:
            isProject = True
            break

    if isAuthor is False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователя-автора с таким ID не существует"
        )
    if isAssignee is False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователя-исполнителя с таким ID не существует"
        )
    if isProject is False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проекта с таким ID не существует"
        )

    new_task = data.dict()
    tasks_db.append(new_task)
    return new_task


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def print_task(task_id: int):
    """
    Выводит одну задачу с соответствующим ID.
    :param task_id: ID задачи
    :return: Задача
    """
    task = None
    for t in tasks_db:
        if t.get("task_id") == task_id:
            task = t
            break

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена"
        )
    return task


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, update_data: TaskUpdate):
    """
    Обновляет задачу по её ID.
    Принимает только те поля, которые нужно изменить.

    :param task_id: ID задачи
    :param update_data: Изменённые данные
    :return: Изменённая задача
    """
    task = None
    for t in tasks_db:
        if t.get("task_id") == task_id:
            task = t
            break

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена"
        )

    # Преобразуем входные данные в словарь, исключая None-поля
    update_dict = update_data.dict(exclude_unset=True)

    for key, value in update_dict.items():
        if value is not None:
            task[key] = value

    return task


@router.delete("/tasks/{task_id}", response_model=TaskResponse)
async def delete_task(task_id: int):
    """
    Удаление задачи с соответствующим ID.
    :param task_id: ID задачи
    :return: Удалённая задача
    """
    task = None
    for t in tasks_db:
        if t.get("task_id") == task_id:
            task = t
            break

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена"
        )
    tasks_db.remove(task)
    return task