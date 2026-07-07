from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.attachment import Attachment


class AttachmentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def create(self, data: dict) -> Attachment:
        attachment = Attachment(**data)
        self.session.add(attachment)
        await self.session.commit()
        await self.session.refresh(attachment)
        return attachment


    async def get_by_task(self, task_id: int) -> list[Attachment]:
        query = select(Attachment).where(Attachment.task_id == task_id)
        result = await self.session.execute(query)
        return result.scalars().all()


    async def get_by_id(self, attachment_id: int) -> Attachment | None:
        query = select(Attachment).where(Attachment.id == attachment_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


    async def delete(self, attachment: Attachment) -> None:
        await self.session.delete(attachment)
        await self.session.commit()