from fastapi import APIRouter
from app.apis.dtos.agent_dto import AgentRequest, AgentResponse
from app.services.agent_service import run_agent

# ============================================================
# [API Layer] Agent 라우팅 영역
# ============================================================

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/query", response_model=AgentResponse)
async def query(request: AgentRequest) -> AgentResponse:
    answer = run_agent(request.query)
    return AgentResponse(query=request.query, answer=answer)
