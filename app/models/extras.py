from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class Comment(Base):
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)

    task_id = Column(Integer, ForeignKey("task.id"), nullable=False)
    task = relationship("Task", back_populates="comments")

    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    author = relationship("User", back_populates="comments")

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Attachment(Base):
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)  # Local storage path

    task_id = Column(Integer, ForeignKey("task.id"), nullable=False)
    task = relationship("Task", back_populates="attachments")

    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())


class Notification(Base):
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)

    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = relationship("User", back_populates="notifications")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
