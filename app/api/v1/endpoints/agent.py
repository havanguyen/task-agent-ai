from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.config import settings
from app.models.user import User
from app.agent.graph import run_agent
from app.core.rag import index_data
from app.schemas.api_response import ApiResponse
from app.schemas.agent import ChatRequest, ChatResponse, SyncResponse

router = APIRouter()


@router.post("/sync-knowledge")
def sync_knowledge_base(
    db: Session = Depends(deps.get_db),
):
    try:
        count = index_data(db)
        data = SyncResponse(indexed_count=count)
        return ApiResponse.success_response(
            data=data, message="Knowledge base updated successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to sync knowledge base: {str(e)}"
        )


@router.post("/chat")
def chat_with_agent(
    request: ChatRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    if not settings.GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")

    try:
        response_text = run_agent(
            user_message=request.message, db=db, current_user=current_user
        )

        data = ChatResponse(response=response_text, actions=[])
        return ApiResponse.success_response(
            data=data, message="Chat response generated"
        )

    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            data = ChatResponse(
                response="⏳ API quota exceeded. Please wait a moment and try again.",
                actions=[],
            )
            return ApiResponse.success_response(data=data, message="Rate limited")
        raise HTTPException(status_code=500, detail=str(e))
