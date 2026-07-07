from pydantic import BaseModel
from datetime import datetime

class AttachmentResponse(BaseModel):
    id: int
    task_id: int
    file_name: str
    file_key: str
    content_type: str | None = None
    size: int | None = None
    bucket_name: str
    created_at: datetime
    uploaded_by_user_id: int | None = None