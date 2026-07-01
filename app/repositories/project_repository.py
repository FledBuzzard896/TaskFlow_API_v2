from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.db.models.projects import Project


class ProjectRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_all(self) -> list[Project]:
        query = select(Project).options(
            selectinload(Project.tasks), selectinload(Project.owner)
        )
        result = await self.session.execute(query)
        return result.scalars().all()


    async def get_by_id(self, project_id: int) -> Project | None:
        query = select(Project).where(Project.id == project_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


    async def create(self, data: dict) -> Project:
        project = Project(**data)
        self.session.add(project)
        try:
            await self.session.commit()
            await self.session.refresh(project)
        except Exception as e:
            await self.session.rollback()
            raise e
        return project


    async def update(self, project_id: int, update_data: dict) -> Project | None:
        project = await self.get_by_id(project_id)
        if not project:
            return None
        for key, value in update_data.items():
            setattr(project, key, value)
        try:
            await self.session.commit()
            await self.session.refresh(project)
        except Exception as e:
            await self.session.rollback()
            raise e
        return project


    async def delete(self, project: Project) -> None:
        try:
            self.session.delete(project)
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise e