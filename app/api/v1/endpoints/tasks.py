from datetime import datetime, timezone
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.api import deps
from app.models.task import Task, TaskStatus, TaskPriority
from app.models.project import Project, ProjectMember
from app.models.user import User, UserRole
from app.models.extras import Comment, Attachment
from app.schemas.task import Task as TaskSchema, TaskCreate, TaskUpdate
from app.services import notification as notification_service

router = APIRouter()


def check_project_membership(db: Session, user: User, project_id: int):
    # Check if project exists and belongs to user's org
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project or project.organization_id != user.organization_id:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check membership
    # Admin/Manager implicitly members? Or strictly explicitly?
    # "Only project members can create or update tasks"
    # Admin is usually superuser. Let's say Admin/Manager can override, but let's stick to "Project Members".
    # Assuming Admin adds themselves if they want to edit.
    # But let's allow Admin/Manager to view/edit for ease.
    if user.role in [UserRole.ADMIN, UserRole.MANAGER]:
        return project

    member = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project_id, ProjectMember.user_id == user.id
        )
        .first()
    )
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this project")
    return project


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
    """
    Retrieve tasks. Filter by project, status, priority, assignee.
    """
    query = db.query(Task)

    # User can only see tasks in their organization
    # And specifically projects they are in? or all org tasks?
    # "List tasks in a project" implies project_id is usually filtered.
    # If no project_id, maybe list all my assigned tasks?

    # Filter by Org via projects
    query = query.join(Project).filter(
        Project.organization_id == current_user.organization_id
    )

    if project_id:
        check_project_membership(db, current_user, project_id)
        query = query.filter(Task.project_id == project_id)

    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    if assignee_id:
        query = query.filter(Task.assignee_id == assignee_id)

    tasks = query.offset(skip).limit(limit).all()
    return tasks


@router.post("/", response_model=TaskSchema)
def create_task(
    *,
    db: Session = Depends(deps.get_db),
    task_in: TaskCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create task.
    "Only project members can create... tasks in that project."
    """
    check_project_membership(db, current_user, task_in.project_id)

    # Assignee check
    # "Only Admin/Manager can assign tasks to others. Members can assign only to themselves."
    if task_in.assignee_id and task_in.assignee_id != current_user.id:
        if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
            raise HTTPException(
                status_code=403, detail="Members can only assign tasks to themselves"
            )
        # Check assignee is in org/project?
        assignee = db.query(User).filter(User.id == task_in.assignee_id).first()
        if not assignee or assignee.organization_id != current_user.organization_id:
            raise HTTPException(status_code=400, detail="Invalid assignee")

    # Due date validation: must be today or in the future
    if task_in.due_date:
        now = datetime.now(timezone.utc)
        if task_in.due_date.replace(tzinfo=timezone.utc) < now.replace(
            hour=0, minute=0, second=0, microsecond=0
        ):
            raise HTTPException(
                status_code=400, detail="Due date must be today or in the future"
            )

    task = Task(
        title=task_in.title,
        description=task_in.description,
        status=task_in.status,
        priority=task_in.priority,
        due_date=task_in.due_date,
        project_id=task_in.project_id,
        assignee_id=task_in.assignee_id
        or current_user.id,  # Default to self if None? OR allowed None.
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    if task.assignee_id and task.assignee_id != current_user.id:
        notification_service.notify_assignee(db, task, task.assignee_id)

    return task


@router.put("/{task_id}", response_model=TaskSchema)
def update_task(
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
    task_in: TaskUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update task.
    Status workflow: todo -> in-progress -> done.
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    check_project_membership(db, current_user, task.project_id)

    # State transition check
    if task_in.status and task_in.status != task.status:
        # todo -> in-progress -> done
        valid = False
        if task.status == TaskStatus.TODO and task_in.status == TaskStatus.IN_PROGRESS:
            valid = True
        elif (
            task.status == TaskStatus.IN_PROGRESS and task_in.status == TaskStatus.DONE
        ):
            valid = True
        # Allow same status? yes.
        # Allow skipping? "not backward".
        # What about Todo -> Done? usually allowed.
        # Rule: "Status workflow: todo -> in-progress -> done (no complex review step)"
        # Rule: "...but not backward."

        # Simple implementation of order
        orders = {TaskStatus.TODO: 1, TaskStatus.IN_PROGRESS: 2, TaskStatus.DONE: 3}
        if orders[task_in.status] < orders[task.status]:
            raise HTTPException(
                status_code=400, detail="Cannot move task status backward"
            )

    # Due date validation: must be today or in the future
    if task_in.due_date:
        now = datetime.now(timezone.utc)
        if task_in.due_date.replace(tzinfo=timezone.utc) < now.replace(
            hour=0, minute=0, second=0, microsecond=0
        ):
            raise HTTPException(
                status_code=400, detail="Due date must be today or in the future"
            )

    # Update fields
    old_status = task.status
    task_data = task_in.dict(exclude_unset=True)
    for field in task_data:
        setattr(task, field, task_data[field])

    db.add(task)
    db.commit()
    db.refresh(task)

    if task.status != old_status:
        notification_service.notify_status_change(db, task)

    return task


@router.post("/{task_id}/comments", response_model=Any)
def create_comment(
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
    content: str,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Add a comment to a task.
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    check_project_membership(db, current_user, task.project_id)

    comment = Comment(content=content, task_id=task_id, user_id=current_user.id)
    db.add(comment)
    db.commit()

    # Notify assignee if someone else commented
    if task.assignee_id and task.assignee_id != current_user.id:
        notification_service.create_notification(
            db,
            task.assignee_id,
            "New Comment",
            f"{current_user.full_name} commented on {task.title}",
        )

    return {"message": "Comment added"}


@router.post("/{task_id}/attachments", response_model=Any)
def upload_attachment(
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Upload attachment.
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    check_project_membership(db, current_user, task.project_id)

    # Check max attachments (max 3 per task)
    existing_count = db.query(Attachment).filter(Attachment.task_id == task_id).count()
    if existing_count >= 3:
        raise HTTPException(
            status_code=400, detail="Maximum 3 attachments per task allowed"
        )

    # Check file size (max 5MB)
    MAX_SIZE_BYTES = 5 * 1024 * 1024  # 5MB
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    if file_size > MAX_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="File size exceeds 5MB limit")

    # Save file
    import os
    import shutil

    os.makedirs("storage", exist_ok=True)
    file_path = f"storage/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    attachment = Attachment(
        filename=file.filename, file_path=file_path, task_id=task_id
    )
    db.add(attachment)
    db.commit()

    return {"message": "Attachment uploaded", "filename": file.filename}
