from datetime import datetime
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api import deps
from app.models.project import Project, ProjectMember
from app.models.task import Task, TaskStatus
from app.models.organization import Organization
from app.models.user import User, UserRole
from app.schemas.project import Project as ProjectSchema, ProjectCreate, ProjectUpdate
from app.schemas.user import User as UserSchema

router = APIRouter()


@router.get("/", response_model=List[ProjectSchema])
def read_projects(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve projects.
    Admin/Manager sees all org projects.
    Members see projects they are members of.
    """
    if current_user.role in [UserRole.ADMIN, UserRole.MANAGER]:
        projects = (
            db.query(Project)
            .filter(Project.organization_id == current_user.organization_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    else:
        # User sees projects they are joined
        # Or should members see all projects but only edit if member?
        # Req: "Members can only participate" usually implies they are added to it.
        # "Project... Can add/remove members."
        # Assuming members only see projects they are added to in the list, OR all open projects?
        # Let's enforce visibility: All org projects visible?
        # Let's say: Admin/Manager sees all. Members might see all to request join?
        # Let's restrictive: Members see only their projects.
        projects = (
            db.query(Project)
            .join(ProjectMember)
            .filter(ProjectMember.user_id == current_user.id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    return projects


@router.post("/", response_model=ProjectSchema)
def create_project(
    *,
    db: Session = Depends(deps.get_db),
    project_in: ProjectCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new project. Only Admin/Manager.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if project_in.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=400, detail="Cannot create project in another organization"
        )

    project = Project(
        name=project_in.name,
        description=project_in.description,
        organization_id=current_user.organization_id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    # Auto-add creator as member?
    member = ProjectMember(project_id=project.id, user_id=current_user.id)
    db.add(member)
    db.commit()

    return project


@router.post("/{project_id}/members", response_model=Any)
def add_project_member(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int,
    user_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Add member to project. Admin/Manager/Project Owner?
    Req: "Project... Can add/remove members."
    Let's allow Admin/Manager of the Org.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=404, detail="Project not found"
        )  # Hide cross-org

    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Check user belongs to org
    user_to_add = db.query(User).filter(User.id == user_id).first()
    if not user_to_add or user_to_add.organization_id != project.organization_id:
        raise HTTPException(status_code=400, detail="User not in organization")

    member = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project_id, ProjectMember.user_id == user_id
        )
        .first()
    )
    if member:
        raise HTTPException(status_code=400, detail="User already in project")

    new_member = ProjectMember(project_id=project_id, user_id=user_id)
    db.add(new_member)
    db.commit()
    return {"message": "Member added"}


@router.get("/{project_id}/stats", response_model=Any)
def get_project_stats(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get task count by status.
    """
    # Verify access first (reusing check logic or manual)
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project or project.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Project not found")

    stats = (
        db.query(Task.status, func.count(Task.id))
        .filter(Task.project_id == project_id)
        .group_by(Task.status)
        .all()
    )

    return {k.value: v for k, v in stats}


@router.get("/{project_id}/overdue", response_model=Any)
def get_overdue_tasks(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get overdue tasks.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project or project.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Project not found")

    tasks = (
        db.query(Task)
        .filter(
            Task.project_id == project_id,
            Task.due_date < datetime.utcnow(),
            Task.status != TaskStatus.DONE,
        )
        .all()
    )

    return tasks
