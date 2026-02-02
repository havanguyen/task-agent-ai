from typing import Any, List, Optional
from sqlalchemy.orm import Session

from app.repositories.base import BaseRepository
from app.models.task import Task, TaskStatus, TaskPriority
from app.models.project import Project
from app.schemas.task import TaskCreate, TaskUpdate


class TaskRepository(BaseRepository[Task, TaskCreate, TaskUpdate]):

    def __init__(self):
        super().__init__(Task)

    def get_by_project(
        self, db: Session, project_id: int, *, skip: int = 0, limit: int = 100
    ) -> List[Task]:
        return (
            db.query(Task)
            .filter(Task.project_id == project_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_organization(
        self,
        db: Session,
        organization_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
        project_id: Optional[int] = None,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        assignee_id: Optional[int] = None
    ) -> List[Task]:
        query = (
            db.query(Task)
            .join(Project)
            .filter(Project.organization_id == organization_id)
        )

        if project_id:
            query = query.filter(Task.project_id == project_id)
        if status:
            query = query.filter(Task.status == status)
        if priority:
            query = query.filter(Task.priority == priority)
        if assignee_id:
            query = query.filter(Task.assignee_id == assignee_id)

        return query.offset(skip).limit(limit).all()

    def get_by_assignee(
        self, db: Session, assignee_id: int, *, skip: int = 0, limit: int = 100
    ) -> List[Task]:
        return (
            db.query(Task)
            .filter(Task.assignee_id == assignee_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_task(
        self,
        db: Session,
        *,
        title: str,
        project_id: int,
        description: Optional[str] = None,
        status: TaskStatus = TaskStatus.TODO,
        priority: TaskPriority = TaskPriority.MEDIUM,
        due_date: Any = None,
        assignee_id: Optional[int] = None
    ) -> Task:
        task = Task(
            title=title,
            description=description,
            status=status,
            priority=priority,
            due_date=due_date,
            project_id=project_id,
            assignee_id=assignee_id,
        )
        db.add(task)
        db.flush()
        db.refresh(task)
        return task

task_repository = TaskRepository()
