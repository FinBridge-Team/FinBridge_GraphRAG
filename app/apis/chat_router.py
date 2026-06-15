from fastapi import APIRouter
from app.apis.dtos.chat_dto import ChatRequest, ChatResponse
from app.services.chat_service import process_chat

# ============================================================
# [API Layer] 라우팅 영역
# ============================================================

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    reply = process_chat(request.session_id, request.message)
    return ChatResponse(reply=reply)
