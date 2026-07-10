from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.attachment_repository import AttachmentRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from app.storage.s3_client import S3Client
from app.core.config import settings


class AttachmentService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.attachment_repo = AttachmentRepository(session)
        self.task_repo = TaskRepository(session)
        self.user_repo = UserRepository(session)
        self.user_service = UserService(session)
        self.s3_client = S3Client()

    async def _check_task_access(self, task_id: int, current_user: dict) -> None:
        """
        Проверяет, имеет ли пользователь доступ к задаче.
        Админ имеет доступ ко всем задачам.
        Обычный пользователь — только к своим.
        """
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")

        # Если пользователь админ — доступ разрешён
        if "admin" in current_user.get("roles", []):
            return

        # Получаем / создаём пользователя
        user = await self.user_service.get_or_create_user(current_user)

        # Проверяем, что пользователь является автором задачи
        if task.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав для доступа к задаче")


    async def upload_file(
            self,
            task_id: int,
            file_content: bytes,
            file_name: str,
            content_type: str,
            current_user: dict
    ) -> dict:
        """Загружает файл и сохраняет метаданные."""
        # Проверяем доступ к задаче
        await self._check_task_access(task_id, current_user)

        # Проверяем размер файла (например, лимит 10 МБ)
        max_size = 10 * 1024 * 1024  # 10 MB
        if len(file_content) > max_size:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File too large (max 10MB)")

        # Загружаем в S3
        file_key = await self.s3_client.upload_file(file_content, file_name, content_type)

        # Получаем пользователя (чтобы заполнить uploaded_by_user_id)
        user = await self.user_service.get_or_create_user(current_user)

        # Сохраняем метаданные в БД
        attachment_data = {
            "task_id": task_id,
            "file_name": file_name,
            "file_key": file_key,
            "content_type": content_type,
            "size": len(file_content),
            "bucket_name": settings.MINIO_BUCKET,
            "uploaded_by_user_id": user.id,
        }
        attachment = await self.attachment_repo.create(attachment_data)
        return attachment


    async def get_attachments_by_task(self, task_id: int, current_user: dict) -> list:
        """Возвращает список вложений задачи (с проверкой доступа)."""
        await self._check_task_access(task_id, current_user)
        return await self.attachment_repo.get_by_task(task_id)


    async def get_download_url(self, task_id: int, attachment_id: int, current_user: dict) -> str:
        """Генерирует временную ссылку для скачивания (с проверкой доступа)."""
        await self._check_task_access(task_id, current_user)

        attachment = await self.attachment_repo.get_by_id(attachment_id)
        if not attachment:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Вложение не найдено")
        if attachment.task_id != task_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Вложение предназначено для другой задачи")
        return await self.s3_client.get_presigned_url(attachment.file_key)


    async def delete_attachment(self, task_id: int, attachment_id: int, current_user: dict) -> None:
        """Удаляет вложение (из S3 и БД) с проверкой доступа."""
        await self._check_task_access(task_id, current_user)

        attachment = await self.attachment_repo.get_by_id(attachment_id)
        if not attachment:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Вложение не найдено")
        if attachment.task_id != task_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Вложение предназначено для другой задачи")

        await self.s3_client.delete_file(attachment.file_key)
        await self.attachment_repo.delete(attachment)