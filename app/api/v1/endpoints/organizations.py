from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.models.organization import Organization
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from app.schemas.organization import (
    Organization as OrganizationSchema,
    OrganizationCreate,
)
from app.schemas.user import UserCreate

router = APIRouter()


@router.post("/", response_model=OrganizationSchema)
def create_organization(
    *,
    db: Session = Depends(deps.get_db),
    org_in: OrganizationCreate,
    # In a real app, this might be open or super-admin only.
    # For this assignment, allowing open creation to bootstrap.
) -> Any:
    """
    Create new organization.
    """
    org = db.query(Organization).filter(Organization.name == org_in.name).first()
    if org:
        raise HTTPException(
            status_code=400,
            detail="The organization with this name already exists",
        )
    db_obj = Organization(name=org_in.name)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


@router.post("/register", response_model=Any)
def register_organization_and_admin(
    *,
    db: Session = Depends(deps.get_db),
    org_name: str,
    email: str,
    password: str,
    full_name: str,
) -> Any:
    """
    Bootstrap endpoint: Create Org and Admin User.
    """
    # 1. Check if org exists
    org = db.query(Organization).filter(Organization.name == org_name).first()
    if org:
        raise HTTPException(status_code=400, detail="Organization exists")

    # 2. Check if user exists (global check, or just this logic)
    user = db.query(User).filter(User.email == email).first()
    if user:
        raise HTTPException(status_code=400, detail="User email exists")

    # 3. Create Org
    new_org = Organization(name=org_name)
    db.add(new_org)
    db.flush()  # get id

    # 4. Create Admin User
    new_user = User(
        email=email,
        hashed_password=get_password_hash(password),
        full_name=full_name,
        role=UserRole.ADMIN,
        organization_id=new_org.id,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Organization and Admin created",
        "organization_id": new_org.id,
        "user_id": new_user.id,
    }
