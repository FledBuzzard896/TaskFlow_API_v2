from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Task
from app.repositories.project_repository import ProjectRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService


class TaskService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.task_repo = TaskRepository(session)
        self.project_repo = ProjectRepository(session)
        self.user_repo = UserRepository(session)
        self.user_service = UserService(session)


    async def _check_task_owner_or_admin(self, task: Task, current_user: dict) -> None:
        """
        Проверяет, что пользователь является владельцем задачи или админом.
        Если нет – выбрасывает 403.
        """
        if "admin" in current_user.get("roles", []):
            return
        user = await self.user_service.get_or_create_user(current_user)
        if task.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав"
            )


    async def get_all_tasks(self, filters: dict, limit: int, offset: int, current_user: dict) -> list[Task]:
        """
        Возвращает список задач с фильтрацией и пагинацией.
        Если пользователь не админ, добавляет фильтр по user_id.
        """
        if "admin" not in current_user.get("roles", []):
            user = await self.user_service.get_or_create_user(current_user)
            filters["user_id"] = user.id
        return await self.task_repo.get_all(filters, limit, offset)


    async def get_task_by_id(self, task_id: int, current_user: dict) -> Task:
        """ Возвращает задачу по ID, проверяя права доступа. """
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Задача не найдена"
            )
        await self._check_task_owner_or_admin(task, current_user)
        return task


    async def create_task(self, data: dict, current_user: dict) -> Task:
        """
        Создаёт новую задачу.
        Подставляет user_id из токена (или создаёт пользователя).
        Проверяет существование проекта и исполнителя (если указаны).
        """
        # Либо создаём, либо берем из БД
        user = await self.user_service.get_or_create_user(current_user)
        data["user_id"] = user.id

        if data.get("project_id") is not None:
            project = await self.project_repo.get_by_id(data["project_id"])
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Проект не найден"
                )
        if data.get("assignee_id") is not None:
            user = await self.user_repo.get_by_id(data["assignee_id"])
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Пользователь не найден"
                )

        return await self.task_repo.create(data)


    async def update_task(self, task_id: int, update_data: dict, current_user: dict) -> Task:
        """
        Обновляет задачу, проверяя права доступа.
        При обновлении project_id или assignee_id проверяет их существование.
        """
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Задача не найдена"
            )

        # Проверка прав
        await self._check_task_owner_or_admin(task, current_user)

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
        return await self.task_repo.update(task, update_data)


    async def delete_task(self, task_id: int, current_user: dict) -> Task:
        """ Удаляет задачу, проверяя права доступа. """
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Задача не найдена"
            )
        await self._check_task_owner_or_admin(task, current_user)
        await self.task_repo.delete(task)
        return task