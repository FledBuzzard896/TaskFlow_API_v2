from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.attachment_repository import AttachmentRepository
from app.repositories.task_repository import TaskRepository
from app.storage.s3_client import S3Client
from app.core.config import settings


class AttachmentService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.attachment_repo = AttachmentRepository(session)
        self.task_repo = TaskRepository(session)
        self.s3_client = S3Client()


    async def upload_file(self, task_id: int, file_content: bytes, file_name: str, content_type: str, uploaded_by_user_id: int) -> dict:
        # Проверяем, что задача существует
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Проверяем размер файла (например, лимит 10 МБ)
        max_size = 10 * 1024 * 1024  # 10 MB
        if len(file_content) > max_size:
            raise HTTPException(status_code=400, detail="File too large (max 10MB)")

        # Загружаем в S3
        file_key = await self.s3_client.upload_file(file_content, file_name, content_type)

        # Сохраняем метаданные в БД
        attachment_data = {
            "task_id": task_id,
            "file_name": file_name,
            "file_key": file_key,
            "content_type": content_type,
            "size": len(file_content),
            "bucket_name": settings.MINIO_BUCKET,
            "uploaded_by_user_id": uploaded_by_user_id,
        }
        attachment = await self.attachment_repo.create(attachment_data)
        return attachment


    async def get_attachments_by_task(self, task_id: int) -> list:
        # Проверяем задачу
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return await self.attachment_repo.get_by_task(task_id)


    async def get_download_url(self, task_id: int, attachment_id: int) -> str:
        attachment = await self.attachment_repo.get_by_id(attachment_id)
        if not attachment:
            raise HTTPException(status_code=404, detail="Attachment not found")
        if attachment.task_id != task_id:
            raise HTTPException(status_code=403, detail="Attachment does not belong to this task")
        return await self.s3_client.get_presigned_url(attachment.file_key)


    async def delete_attachment(self, task_id: int, attachment_id: int) -> None:
        attachment = await self.attachment_repo.get_by_id(attachment_id)
        if not attachment:
            raise HTTPException(status_code=404, detail="Attachment not found")
        if attachment.task_id != task_id:
            raise HTTPException(status_code=403, detail="Attachment does not belong to this task")
        await self.s3_client.delete_file(attachment.file_key)
        await self.attachment_repo.delete(attachment)