
from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User
from app.schemas.project import Project as ProjectSchema, ProjectCreate
from app.services import project_service

router = APIRouter()


@router.get("/", response_model=List[ProjectSchema])
def read_projects(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    return project_service.list_projects(db, current_user, skip=skip, limit=limit)


@router.post("/", response_model=ProjectSchema)
def create_project(
    *,
    db: Session = Depends(deps.get_db),
    project_in: ProjectCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    return project_service.create_project(db, current_user, project_in)


@router.post("/{project_id}/members", response_model=Any)
def add_project_member(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int,
    user_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    return project_service.add_member(db, current_user, project_id, user_id)


@router.get("/{project_id}/stats", response_model=Any)
def get_project_stats(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    return project_service.get_stats(db, current_user, project_id)


@router.get("/{project_id}/overdue", response_model=Any)
def get_overdue_tasks(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    return project_service.get_overdue_tasks(db, current_user, project_id)
