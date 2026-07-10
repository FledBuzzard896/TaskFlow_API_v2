from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_db
from app.services.attachment_service import AttachmentService
from app.schemas.attachment import AttachmentResponse

router = APIRouter(tags=["attachments"])


@router.post("/tasks/{task_id}/attachments", response_model=AttachmentResponse, status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    task_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = AttachmentService(db)
    content = await file.read()
    attachment = await service.upload_file(
        task_id=task_id,
        file_content=content,
        file_name=file.filename,
        content_type=file.content_type,
        current_user=current_user,
    )
    return attachment


@router.get("/tasks/{task_id}/attachments", response_model=List[AttachmentResponse])
async def list_attachments(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = AttachmentService(db)
    attachments = await service.get_attachments_by_task(task_id, current_user)
    return attachments


@router.get("/tasks/{task_id}/attachments/{attachment_id}/download")
async def download_attachment(
    task_id: int,
    attachment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = AttachmentService(db)
    url = await service.get_download_url(task_id, attachment_id, current_user)
    return {"download_url": url}


@router.delete("/tasks/{task_id}/attachments/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attachment(
    task_id: int,
    attachment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = AttachmentService(db)
    await service.delete_attachment(task_id, attachment_id, current_user)
    return None