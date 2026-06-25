from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.models.tasks import Task


class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_all(self, filters: dict, limit: int, offset: int):
        query = select(Task)
        # Фильтрация
        if filters.get("status"):
            query = query.where(Task.status == filters["status"])
        if filters.get("project_id"):
            query = query.where(Task.project_id == filters["project_id"])
        if filters.get("priority"):
            query = query.where(Task.priority == filters["priority"])
        if filters.get("assignee_id"):
            query = query.where(Task.assignee_id == filters["assignee_id"])
        # Пагинация
        query = query.offset(offset).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()


    async def get_by_id(self, task_id: int):
        query = select(Task).where(Task.id == task_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


    async def create(self, data: dict):
        task = Task(**data)
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task


    async def update(self, task_id: int, update_data: dict):
        task = await self.get_by_id(task_id)
        if not task:
            return None
        for key, value in update_data.items():
            setattr(task, key, value)
        await self.session.commit()
        await self.session.refresh(task)
        return task


    async def delete(self, task: Task):
        self.session.delete(task)
        await self.session.commit()
        return task