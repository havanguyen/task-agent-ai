

from typing import Any, List
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.task import Task
from app.models.user import User, UserRole
from app.repositories import (
    project_repository,
    project_member_repository,
    user_repository,
)
from app.schemas.project import ProjectCreate


class ProjectService:

    def list_projects(
        self, db: Session, user: User, *, skip: int = 0, limit: int = 100
    ) -> List[Project]:
        if user.role in [UserRole.ADMIN, UserRole.MANAGER]:
            return project_repository.get_by_organization(
                db, user.organization_id, skip=skip, limit=limit
            )
        else:
            return project_repository.get_member_projects(
                db, user.id, skip=skip, limit=limit
            )

    def create_project(
        self, db: Session, user: User, project_in: ProjectCreate
    ) -> Project:
        if user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
            raise HTTPException(status_code=403, detail="Not enough permissions")

        if project_in.organization_id != user.organization_id:
            raise HTTPException(
                status_code=400, detail="Cannot create project in another organization"
            )

        project = project_repository.create_project(
            db,
            name=project_in.name,
            description=project_in.description,
            organization_id=user.organization_id,
        )

        project_member_repository.add_member(db, project.id, user.id)
        db.commit()
        db.refresh(project)

        return project

    def add_member(
        self, db: Session, user: User, project_id: int, user_id: int
    ) -> dict:
        project = project_repository.get(db, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        if project.organization_id != user.organization_id:
            raise HTTPException(status_code=404, detail="Project not found")

        if user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
            raise HTTPException(status_code=403, detail="Not enough permissions")

        user_to_add = user_repository.get(db, user_id)
        if not user_to_add or user_to_add.organization_id != project.organization_id:
            raise HTTPException(status_code=400, detail="User not in organization")

        if project_member_repository.is_member(db, project_id, user_id):
            raise HTTPException(status_code=400, detail="User already in project")

        project_member_repository.add_member(db, project_id, user_id)
        db.commit()

        return {"message": "Member added"}

    def get_stats(self, db: Session, user: User, project_id: int) -> dict:
        project = project_repository.get(db, project_id)
        if not project or project.organization_id != user.organization_id:
            raise HTTPException(status_code=404, detail="Project not found")

        return project_repository.get_task_stats(db, project_id)

    def get_overdue_tasks(self, db: Session, user: User, project_id: int) -> List[Task]:
        project = project_repository.get(db, project_id)
        if not project or project.organization_id != user.organization_id:
            raise HTTPException(status_code=404, detail="Project not found")

        return project_repository.get_overdue_tasks(db, project_id)

project_service = ProjectService()
