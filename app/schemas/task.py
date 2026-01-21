from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from app.models.task import TaskStatus, TaskPriority
from app.schemas.user import User


# Shared properties
class TaskBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = TaskStatus.TODO
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None
    assignee_id: Optional[int] = None


# Properties to receive on creation
class TaskCreate(TaskBase):
    title: str
    project_id: int


# Properties to receive on update
class TaskUpdate(TaskBase):
    pass


# Properties shared by models stored in DB
class TaskInDBBase(TaskBase):
    id: int
    project_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# Properties to return to client
class Task(TaskInDBBase):
    assignee: Optional[User] = None


# Properties stored in DB
class TaskInDB(TaskInDBBase):
    pass
