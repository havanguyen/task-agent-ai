from typing import Optional, List
from pydantic import BaseModel


# Shared properties
class OrganizationBase(BaseModel):
    name: Optional[str] = None


# Properties to receive on organization creation
class OrganizationCreate(OrganizationBase):
    name: str


# Properties to receive on organization update
class OrganizationUpdate(OrganizationBase):
    pass


# Properties shared by models stored in DB
class OrganizationInDBBase(OrganizationBase):
    id: int
    name: str

    model_config = {"from_attributes": True}


# Properties to return to client
class Organization(OrganizationInDBBase):
    pass


# Properties stored in DB
class OrganizationInDB(OrganizationInDBBase):
    pass
