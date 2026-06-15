from app.services.agent_service import run_agent

# ============================================================
# [Service Layer] 챗봇 인터페이스 영역
# 세션별 대화 히스토리를 메모리에 유지 (샘플용)
# ============================================================

_history: dict[str, list[str]] = {}  # session_id → 대화 목록


def process_chat(session_id: str, message: str) -> str:
    history = _history.get(session_id, [])

    answer = run_agent(message, history)

    history.append(f"사용자: {message}")
    history.append(f"AI: {answer}")
    _history[session_id] = history[-10:]  # 최근 5턴(10줄)만 유지

    return answer
