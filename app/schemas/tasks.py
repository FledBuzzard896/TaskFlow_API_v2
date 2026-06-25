from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

from app.core.enums import TaskPriority, TaskStatus


class TaskBase(BaseModel):
    title: str = Field(..., description="Название задачи")
    description: Optional[str] = Field(None, description="Описание задачи")
    deadline: Optional[datetime] = Field(None, description="Дедлайн задачи")
    project_id: int = Field(..., description="ID проекта")
    priority: TaskPriority = Field(TaskPriority.MEDIUM, description="Приоритет")

class TaskCreate(TaskBase):
    status: TaskStatus = Field(TaskStatus.IN_PROGRESS, description="Статус задачи")
    user_id: Optional[int] = Field(None, description="Автор задачи")
    assignee_id: Optional[int] = Field(None, description="Исполнитель задачи")

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    deadline: Optional[datetime] = None
    priority: Optional[TaskPriority] = None
    assignee_id: Optional[int] = None

class TaskResponse(TaskBase):
    id: int
    user_id: Optional[int]
    assignee_id: Optional[int]
    status: TaskStatus
