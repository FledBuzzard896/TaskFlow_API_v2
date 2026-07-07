from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.attachment_service import AttachmentService
from app.schemas.attachment import AttachmentResponse

router = APIRouter(tags=["attachments"])


@router.post("/tasks/{task_id}/attachments", response_model=AttachmentResponse, status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    task_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    # Временно user_id = 1, позже будет из токена
    user_id = 1
    service = AttachmentService(db)
    attachment = await service.upload_file(
        task_id=task_id,
        file_content=await file.read(),
        file_name=file.filename,
        content_type=file.content_type,
        uploaded_by_user_id=user_id
    )
    return attachment


@router.get("/tasks/{task_id}/attachments", response_model=List[AttachmentResponse])
async def list_attachments(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = AttachmentService(db)
    attachments = await service.get_attachments_by_task(task_id)
    return attachments


@router.get("/tasks/{task_id}/attachments/{attachment_id}/download")
async def download_attachment(
    task_id: int,
    attachment_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = AttachmentService(db)
    url = await service.get_download_url(task_id, attachment_id)
    return {"download_url": url}


@router.delete("/tasks/{task_id}/attachments/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attachment(
    task_id: int,
    attachment_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = AttachmentService(db)
    await service.delete_attachment(task_id, attachment_id)
    return None