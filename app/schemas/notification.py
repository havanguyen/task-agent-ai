from pydantic import BaseModel


class NotificationBase(BaseModel):
    title: str
    message: str


class Notification(BaseModel):
    id: int
    title: str
    message: str
    is_read: bool

    model_config = {"from_attributes": True}
