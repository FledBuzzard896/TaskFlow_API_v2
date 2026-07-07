from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Attachment(Base):
    __tablename__ = 'attachment'

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, index=True)
    file_name = Column(String, nullable=False)
    file_key = Column(String, nullable=False, unique=True)  # уникальный идентификатор в S3
    content_type = Column(String, nullable=True)
    size = Column(Integer, nullable=True)  # размер в байтах
    bucket_name = Column(String, nullable=False, default="taskflow-files")
    created_at = Column(DateTime, server_default=func.now())
    uploaded_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    # Отношения
    task = relationship("Task", back_populates="attachments")
    uploaded_by = relationship("User", foreign_keys=[uploaded_by_user_id])