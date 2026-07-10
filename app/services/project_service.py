from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Project
from app.repositories.project_repository import ProjectRepository
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService


class ProjectService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.project_repo = ProjectRepository(session)
        self.user_repo = UserRepository(session)
        self.user_service = UserService(session)


    async def _check_owner_or_admin(self, project: Project, current_user: dict) -> None:
        """Проверяет, является ли пользователь владельцем проекта или админом."""
        if "admin" in current_user.get("roles", []):
            return
        user = await self.user_service.get_or_create_user(current_user)
        if project.owner_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав")


    async def get_all_projects(self, current_user: dict) -> list[Project]:
        """Возвращает все проекты (админ) или только свои."""
        if "admin" in current_user.get("roles", []):
            return await self.project_repo.get_all()
        # Иначе фильтруем по владельцу
        user = await self.user_service.get_or_create_user(current_user)
        return await self.project_repo.get_by_owner(user.id)


    async def get_by_id(self, project_id: int, current_user: dict) -> Project | None:
        """ Возвращает проект по ID, проверяя права доступа. """
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Проект с таким ID не найден"
            )
        await self._check_owner_or_admin(project, current_user)
        return project


    async def create_project(self, data: dict, current_user: dict) -> Project:
        """
        Создаёт новый проект.
        Подставляет owner_id из токена (или создаёт пользователя).
        """
        user = await self.user_service.get_or_create_user(current_user)
        data["owner_id"] = user.id
        return await self.project_repo.create(data)


    async def update_project(self, project_id: int, update_data: dict, current_user: dict) -> Project:
        """ Обновляет проект, проверяя права доступа. """
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Проект не найден")
        await self._check_owner_or_admin(project, current_user)
        return await self.project_repo.update(project, update_data)


    async def delete_project(self, project_id: int, current_user: dict) -> Project:
        """ Удаляет проект, проверяя права доступа. """
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Проект не найден")
        await self._check_owner_or_admin(project, current_user)
        await self.project_repo.delete(project)
        return project
