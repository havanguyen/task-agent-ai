from typing import Optional
from pydantic import BaseModel


class OrganizationBase(BaseModel):
    name: Optional[str] = None

class OrganizationCreate(OrganizationBase):
    name: str


class OrganizationUpdate(OrganizationBase):
    pass


class OrganizationInDBBase(OrganizationBase):
    id: int
    name: str
    model_config = {"from_attributes": True}


class Organization(OrganizationInDBBase):
    pass

class OrganizationInDB(OrganizationInDBBase):
    pass
