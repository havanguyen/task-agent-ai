from pydantic import BaseModel


class Organization(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class OrganizationCreate(BaseModel):
    name: str


class OrganizationUpdate(BaseModel):
    name: str


class RegisterRequest(BaseModel):
    organization_name: str
    email: str
    password: str
    full_name: str


class RegisterResponse(BaseModel):
    organization_id: int
    user_id: int
