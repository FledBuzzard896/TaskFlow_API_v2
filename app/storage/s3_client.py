import io
import uuid
from typing import Optional
from aiobotocore.session import get_session
from app.core.config import settings


class S3Client:
    def __init__(self):
        self.endpoint_url = f"http://{settings.MINIO_HOST}:{settings.MINIO_PORT}"
        self.access_key = settings.MINIO_ACCESS_KEY
        self.secret_key = settings.MINIO_SECRET_KEY
        self.bucket_name = settings.MINIO_BUCKET
        self.secure = settings.MINIO_SECURE


    async def upload_file(
        self,
        file_content: bytes,
        file_name: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        """Загружает файл в S3 и возвращает уникальный ключ (file_key)."""
        # Генерируем уникальный ключ: task_<uuid>/<original_filename>
        file_key = f"{uuid.uuid4()}/{file_name}"

        session = await get_session()
        async with session.create_client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            use_ssl=self.secure,
        ) as client:
            await client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_content,
                ContentType=content_type,
            )
        return file_key


    async def get_presigned_url(self, file_key: str, expires: int = 3600) -> str:
        """Генерирует временную ссылку для скачивания файла."""
        session = get_session()
        async with session.create_client(
                "s3",
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                use_ssl=self.secure,
        ) as client:
            url = await client.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": self.bucket_name, "Key": file_key},
                ExpiresIn=expires,
            )
        return url


    async def delete_file(self, file_key: str) -> None:
        """Удаляет файл из S3."""
        session = get_session()
        async with session.create_client(
                "s3",
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                use_ssl=self.secure,
        ) as client:
            await client.delete_object(Bucket=self.bucket_name, Key=file_key)