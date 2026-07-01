from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import TaskStatus
from app.db.models import Task
from app.repositories.project_repository import ProjectRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository


class TaskService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.task_repo = TaskRepository(session)
        self.project_repo = ProjectRepository(session)
        self.user_repo = UserRepository(session)


    async def get_all_tasks(self, filters: dict, limit: int, offset: int) -> list[Task]:
        return await self.task_repo.get_all(filters, limit, offset)


    async def get_task_by_id(self, task_id: int) -> Task:
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Задача не найдена"
            )
        return task


    async def create_task(self, data: dict) -> Task:
        if data.get("project_id"):
            project = await self.project_repo.get_by_id(data["project_id"])
            if not project:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Проект не найден")
        if data.get("assignee_id"):
            user = await self.user_repo.get_by_id(data["assignee_id"])
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
        if data.get("author_id"):
            user = await self.user_repo.get_by_id(data["author_id"])
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
        return await self.task_repo.create(data)


    async def update_task(self, task_id: int, update_data: dict) -> Task:
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Задача не найдена"
            )
        # Проверка нового проекта, если он передан
        if "project_id" in update_data and update_data["project_id"] is not None:
            project = await self.project_repo.get_by_id(update_data["project_id"])
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Проект с таким ID не найден"
                )
        # Проверка нового исполнителя, если он передан
        if "assignee_id" in update_data and update_data["assignee_id"] is not None:
            user = await self.user_repo.get_by_id(update_data["assignee_id"])
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Исполнитель с таким ID не найден"
                )
        # Обновляем поля
        for key, value in update_data.items():
            setattr(task, key, value)
        return await self.task_repo.update(task)


    async def delete_task(self, task_id: int) -> Task:
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")
        await self.task_repo.delete(task)
        return task