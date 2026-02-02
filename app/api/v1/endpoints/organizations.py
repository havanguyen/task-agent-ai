from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.organization import (
    Organization as OrganizationSchema,
    OrganizationCreate,
    RegisterRequest,
    RegisterResponse,
)
from app.schemas.api_response import ApiResponse
from app.services import organization_service

router = APIRouter()


@router.post("/")
def create_organization(
    *,
    db: Session = Depends(deps.get_db),
    org_in: OrganizationCreate,
):
    org = organization_service.create_organization(db, org_in)
    return ApiResponse.success_response(
        data=org, message="Organization created successfully", status_code=201
    )


@router.post("/register")
def register_organization_and_admin(
    *,
    db: Session = Depends(deps.get_db),
    request: RegisterRequest,
):
    result = organization_service.register_with_admin(
        db,
        organization_name=request.organization_name,
        email=request.email,
        password=request.password,
        full_name=request.full_name,
    )
    return ApiResponse.success_response(
        data=result, message="Organization and Admin created", status_code=201
    )
