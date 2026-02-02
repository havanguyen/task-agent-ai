from typing import List

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str


class ActionResult(BaseModel):
    action: str
    success: bool
    details: str


class ChatResponse(BaseModel):
    response: str
    actions: List[ActionResult] = []


class SyncResponse(BaseModel):
    indexed_count: int
