

from typing import Any, List, Optional
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.api import deps
from app.models.task import TaskStatus, TaskPriority
from app.models.user import User
from app.schemas.task import Task as TaskSchema, TaskCreate, TaskUpdate
from app.services import task_service

router = APIRouter()


@router.get("/", response_model=List[TaskSchema])
def read_tasks(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    project_id: Optional[int] = None,
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    assignee_id: Optional[int] = None,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    return task_service.list_tasks(
        db,
        current_user,
        skip=skip,
        limit=limit,
        project_id=project_id,
        status=status,
        priority=priority,
        assignee_id=assignee_id,
    )


@router.post("/", response_model=TaskSchema)
def create_task(
    *,
    db: Session = Depends(deps.get_db),
    task_in: TaskCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    return task_service.create_task(db, current_user, task_in)


@router.put("/{task_id}", response_model=TaskSchema)
def update_task(
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
    task_in: TaskUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    return task_service.update_task(db, current_user, task_id, task_in)


@router.post("/{task_id}/comments", response_model=Any)
def create_comment(
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
    content: str,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    return task_service.add_comment(db, current_user, task_id, content)


@router.post("/{task_id}/attachments", response_model=Any)
def upload_attachment(
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    return task_service.add_attachment(db, current_user, task_id, file)
