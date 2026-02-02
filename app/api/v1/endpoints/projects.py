from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User
from app.schemas.project import (
    Project as ProjectSchema,
    ProjectCreate,
    AddMemberRequest,
)
from app.schemas.api_response import ApiResponse
from app.services import project_service

router = APIRouter()


@router.get("/")
def read_projects(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
):
    projects = project_service.list_projects(db, current_user, skip=skip, limit=limit)
    return ApiResponse.success_response(
        data=projects, message="Projects retrieved successfully"
    )


@router.post("/")
def create_project(
    *,
    db: Session = Depends(deps.get_db),
    project_in: ProjectCreate,
    current_user: User = Depends(deps.get_current_active_user),
):
    project = project_service.create_project(db, current_user, project_in)
    return ApiResponse.success_response(
        data=project, message="Project created successfully", status_code=201
    )


@router.post("/{project_id}/members")
def add_project_member(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int,
    member_in: AddMemberRequest,
    current_user: User = Depends(deps.get_current_active_user),
):
    result = project_service.add_member(db, current_user, project_id, member_in.user_id)
    return ApiResponse.success_response(
        data=result, message="Member added successfully", status_code=201
    )


@router.get("/{project_id}/stats")
def get_project_stats(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int,
    current_user: User = Depends(deps.get_current_active_user),
):
    stats = project_service.get_stats(db, current_user, project_id)
    return ApiResponse.success_response(
        data=stats, message="Project stats retrieved successfully"
    )


@router.get("/{project_id}/overdue")
def get_overdue_tasks(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int,
    current_user: User = Depends(deps.get_current_active_user),
):
    tasks = project_service.get_overdue_tasks(db, current_user, project_id)
    return ApiResponse.success_response(
        data=tasks, message="Overdue tasks retrieved successfully"
    )
