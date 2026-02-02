import os
import shutil
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.models.task import Task, TaskStatus, TaskPriority
from app.models.user import User, UserRole
from app.repositories import (
    task_repository,
    project_repository,
    project_member_repository,
)
from app.repositories.notification_repository import (
    create_comment,
    count_by_task,
    create_attachment,
)
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.notification import create_notification


class TaskService:

    def check_project_membership(self, db: Session, user: User, project_id: int):
        project = project_repository.get(db, project_id)
        if not project or project.organization_id != user.organization_id:
            raise HTTPException(status_code=404, detail="Project not found")

        if user.role in [UserRole.ADMIN, UserRole.MANAGER]:
            return project

        if not project_member_repository.is_member(db, project_id, user.id):
            raise HTTPException(status_code=403, detail="Not a member of this project")

        return project

    def list_tasks(
        self,
        db: Session,
        user: User,
        *,
        skip: int = 0,
        limit: int = 100,
        project_id: Optional[int] = None,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        assignee_id: Optional[int] = None,
    ) -> List[Task]:
        if project_id:
            self.check_project_membership(db, user, project_id)

        return task_repository.get_by_organization(
            db,
            user.organization_id,
            skip=skip,
            limit=limit,
            project_id=project_id,
            status=status,
            priority=priority,
            assignee_id=assignee_id,
        )

    def create_task(self, db: Session, user: User, task_in: TaskCreate) -> Task:
        self.check_project_membership(db, user, task_in.project_id)
        if task_in.assignee_id and task_in.assignee_id != user.id:
            if user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
                raise HTTPException(
                    status_code=403,
                    detail="Members can only assign tasks to themselves",
                )
            from app.repositories import user_repository

            assignee = user_repository.get(db, task_in.assignee_id)
            if not assignee or assignee.organization_id != user.organization_id:
                raise HTTPException(status_code=400, detail="Invalid assignee")
        if task_in.due_date:
            self._validate_due_date(task_in.due_date)

        task = task_repository.create_task(
            db,
            title=task_in.title,
            description=task_in.description,
            status=task_in.status or TaskStatus.TODO,
            priority=task_in.priority or TaskPriority.MEDIUM,
            due_date=task_in.due_date,
            project_id=task_in.project_id,
            assignee_id=task_in.assignee_id or user.id,
        )
        db.commit()
        db.refresh(task)

        if task.assignee_id and task.assignee_id != user.id:
            from app.services.notification_service import notification_service

            notification_service.notify_assignee(db, task, task.assignee_id)

        return task

    def update_task(
        self, db: Session, user: User, task_id: int, task_in: TaskUpdate
    ) -> Task:
        task = task_repository.get(db, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        self.check_project_membership(db, user, task.project_id)

        if task_in.status and task_in.status != task.status:
            self._validate_status_transition(task.status, task_in.status)

        if task_in.due_date:
            self._validate_due_date(task_in.due_date)

        old_status = task.status
        task_data = task_in.model_dump(exclude_unset=True)
        for field, value in task_data.items():
            setattr(task, field, value)

        db.add(task)
        db.commit()
        db.refresh(task)

        if task.status != old_status:
            from app.services.notification_service import notification_service

            notification_service.notify_status_change(db, task)

        return task

    def add_comment(self, db: Session, user: User, task_id: int, content: str) -> dict:
        task = task_repository.get(db, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        self.check_project_membership(db, user, task.project_id)

        create_comment(db, content=content, task_id=task_id, user_id=user.id)
        db.commit()

        if task.assignee_id and task.assignee_id != user.id:
            from app.services.notification_service import notification_service

            create_notification(
                db,
                task.assignee_id,
                "New Comment",
                f"{user.full_name} commented on {task.title}",
            )

        return {"message": "Comment added"}

    def add_attachment(
        self, db: Session, user: User, task_id: int, file: UploadFile
    ) -> dict:
        task = task_repository.get(db, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        self.check_project_membership(db, user, task.project_id)

        existing_count = count_by_task(db, task_id)
        if existing_count >= 3:
            raise HTTPException(
                status_code=400, detail="Maximum 3 attachments per task allowed"
            )

        MAX_SIZE_BYTES = 5 * 1024 * 1024
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        if file_size > MAX_SIZE_BYTES:
            raise HTTPException(status_code=400, detail="File size exceeds 5MB limit")

        os.makedirs("storage", exist_ok=True)
        file_path = f"storage/{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        create_attachment(
            db, filename=file.filename, file_path=file_path, task_id=task_id
        )
        db.commit()

        return {"message": "Attachment uploaded", "filename": file.filename}

    def _validate_due_date(self, due_date: datetime) -> None:
        now = datetime.now(timezone.utc)
        due_date_utc = due_date.replace(tzinfo=timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        if due_date_utc < today_start:
            raise HTTPException(
                status_code=400, detail="Due date must be today or in the future"
            )

    def _validate_status_transition(
        self, current_status: TaskStatus, new_status: TaskStatus
    ) -> None:
        orders = {TaskStatus.TODO: 1, TaskStatus.IN_PROGRESS: 2, TaskStatus.DONE: 3}
        if orders[new_status] < orders[current_status]:
            raise HTTPException(
                status_code=400, detail="Cannot move task status backward"
            )


task_service = TaskService()
