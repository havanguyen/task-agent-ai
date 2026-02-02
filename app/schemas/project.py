from typing import Optional, List
from pydantic import BaseModel
from app.schemas.user import User


class ProjectBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    name: str
    organization_id: int


class ProjectUpdate(ProjectBase):
    pass


class ProjectInDBBase(ProjectBase):
    id: int
    organization_id: int

    model_config = {"from_attributes": True}


class Project(ProjectInDBBase):
    members: List[User] = []


class ProjectInDB(ProjectInDBBase):
    pass
