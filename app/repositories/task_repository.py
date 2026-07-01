from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.db.models.tasks import Task


class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_all(self, filters: dict, limit: int, offset: int) -> list[Task]:
        query = select(Task).options(
            selectinload(Task.project), selectinload(Task.assignee)
        )

        # Фильтрация
        if "status" in filters:
            query = query.where(Task.status == filters["status"])
        if "project_id" in filters:
            query = query.where(Task.project_id == filters["project_id"])
        if "priority" in filters:
            query = query.where(Task.priority == filters["priority"])
        if "assignee_id" in filters:
            query = query.where(Task.assignee_id == filters["assignee_id"])
        # Пагинация
        query = query.offset(offset).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()


    async def get_by_id(self, task_id: int) -> Task | None:
        query = select(Task).where(Task.id == task_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


    async def create(self, data: dict) -> Task:
        task = Task(**data)
        self.session.add(task)
        try:
            await self.session.commit()
            await self.session.refresh(task)
        except Exception as e:
            await self.session.rollback()
            raise e
        return task


    async def update(self, task_id: int, update_data: dict) -> Task | None:
        task = await self.get_by_id(task_id)
        if not task:
            return None
        for key, value in update_data.items():
            setattr(task, key, value)
        try:
            await self.session.commit()
            await self.session.refresh(task)
        except Exception as e:
            await self.session.rollback()
            raise e
        return task


    async def delete(self, task: Task) -> None:
        try:
            self.session.delete(task)
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise e