from typing import Optional

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.api import deps
from app.models.task import TaskStatus, TaskPriority
from app.models.user import User
from app.schemas.task import Task as TaskSchema, TaskCreate, TaskUpdate, CommentCreate
from app.schemas.api_response import ApiResponse
from app.services import task_service

router = APIRouter()


@router.get("/")
def read_tasks(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    project_id: Optional[int] = None,
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    assignee_id: Optional[int] = None,
    current_user: User = Depends(deps.get_current_active_user),
):
    tasks = task_service.list_tasks(
        db,
        current_user,
        skip=skip,
        limit=limit,
        project_id=project_id,
        status=status,
        priority=priority,
        assignee_id=assignee_id,
    )
    return ApiResponse.success_response(
        data=tasks, message="Tasks retrieved successfully"
    )


@router.post("/")
def create_task(
    *,
    db: Session = Depends(deps.get_db),
    task_in: TaskCreate,
    current_user: User = Depends(deps.get_current_active_user),
):
    task = task_service.create_task(db, current_user, task_in)
    return ApiResponse.success_response(
        data=task, message="Task created successfully", status_code=201
    )


@router.put("/{task_id}")
def update_task(
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
    task_in: TaskUpdate,
    current_user: User = Depends(deps.get_current_active_user),
):
    task = task_service.update_task(db, current_user, task_id, task_in)
    return ApiResponse.success_response(data=task, message="Task updated successfully")


@router.post("/{task_id}/comments")
def create_comment(
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
    comment_in: CommentCreate,
    current_user: User = Depends(deps.get_current_active_user),
):
    result = task_service.add_comment(db, current_user, task_id, comment_in.content)
    return ApiResponse.success_response(
        data=result, message="Comment added successfully", status_code=201
    )


@router.post("/{task_id}/attachments")
def upload_attachment(
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_active_user),
):
    result = task_service.add_attachment(db, current_user, task_id, file)
    return ApiResponse.success_response(
        data=result, message="Attachment uploaded successfully", status_code=201
    )
