from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, func
from sqlalchemy.orm import relationship

from app.core.enums import TaskStatus
from app.db.base import Base


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(String)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.IN_PLAN)
    deadline = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    project_id = Column(Integer, ForeignKey("projects.id"), index=True)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    # связи (опционально)
    project = relationship("Project", back_populates="tasks")
    assignee = relationship("User", foreign_keys=[assignee_id])