from typing import Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.repositories.base import BaseRepository
from app.models.project import Project, ProjectMember
from app.models.task import Task, TaskStatus
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectRepository(BaseRepository[Project, ProjectCreate, ProjectUpdate]):

    def __init__(self):
        super().__init__(Project)

    def get_by_organization(
        self, db: Session, organization_id: int, *, skip: int = 0, limit: int = 100
    ) -> List[Project]:
        return (
            db.query(Project)
            .filter(Project.organization_id == organization_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_member_projects(
        self, db: Session, user_id: int, *, skip: int = 0, limit: int = 100
    ) -> List[Project]:
        return (
            db.query(Project)
            .join(ProjectMember)
            .filter(ProjectMember.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_project(
        self,
        db: Session,
        *,
        name: str,
        organization_id: int,
        description: Optional[str] = None
    ) -> Project:
        project = Project(
            name=name, description=description, organization_id=organization_id
        )
        db.add(project)
        db.flush()
        db.refresh(project)
        return project

    def get_task_stats(self, db: Session, project_id: int) -> dict:
        stats = (
            db.query(Task.status, func.count(Task.id))
            .filter(Task.project_id == project_id)
            .group_by(Task.status)
            .all()
        )
        return {k.value: v for k, v in stats}

    def get_overdue_tasks(self, db: Session, project_id: int) -> list[type[Task]]:
        return (
            db.query(Task)
            .filter(
                Task.project_id == project_id,
                Task.due_date < datetime.utcnow(),
                Task.status != TaskStatus.DONE,
            )
            .all()
        )


class ProjectMemberRepository:

    def get_member(
        self, db: Session, project_id: int, user_id: int
    ) -> Optional[ProjectMember]:
        return (
            db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id, ProjectMember.user_id == user_id
            )
            .first()
        )

    def add_member(self, db: Session, project_id: int, user_id: int) -> ProjectMember:
        member = ProjectMember(project_id=project_id, user_id=user_id)
        db.add(member)
        db.flush()
        return member

    def is_member(self, db: Session, project_id: int, user_id: int) -> bool:
        return self.get_member(db, project_id, user_id) is not None


project_repository = ProjectRepository()
project_member_repository = ProjectMemberRepository()
