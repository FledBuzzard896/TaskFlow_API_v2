from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Project
from app.repositories.project_repository import ProjectRepository
from app.repositories.user_repository import UserRepository

class ProjectService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.project_repo = ProjectRepository(session)
        self.user_repo = UserRepository(session)


    async def get_all_projects(self) -> list[Project]:
        return await self.project_repo.get_all()


    async def get_by_id(self, project_id: int) -> Project | None:
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Проект с таким ID не найден"
            )
        return project


    async def create_project(self, data: dict) -> Project:
        # Проверка существования владельца, если передан owner_id
        if data.get("owner_id") is not None:
            user = await self.user_repo.get_by_id(data["owner_id"])
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Пользователь с таким ID не найден"
                )
        # Если owner_id не передан (null) — пропускаем проверку
        return await self.project_repo.create(data)


    async def update_project(self, project_id: int, update_data: dict) -> Project:
        # Получаем проект
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Проект не найден")
        # Передаём объект и словарь изменений в репозиторий
        return await self.project_repo.update(project, update_data)


    async def delete_project(self, project_id: int) -> Project:
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Проект не найден")
        await self.project_repo.delete(project)
        return project