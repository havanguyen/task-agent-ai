from typing import Optional, List
from pydantic import BaseModel
from app.schemas.user import User


# Shared properties
class ProjectBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


# Properties to receive on creation
class ProjectCreate(ProjectBase):
    name: str
    organization_id: int


# Properties to receive on update
class ProjectUpdate(ProjectBase):
    pass


# Properties shared by models stored in DB
class ProjectInDBBase(ProjectBase):
    id: int
    organization_id: int

    model_config = {"from_attributes": True}


# Properties to return to client
class Project(ProjectInDBBase):
    members: List[User] = []


# Properties stored in DB
class ProjectInDB(ProjectInDBBase):
    pass
