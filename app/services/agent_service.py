from app.adapters.gemini_adapter import call_gemini
from app.adapters.mock_data_adapter import get_external_news, get_db_stock_data

# ============================================================
# [Service Layer] Agent 오케스트레이션 영역
# 1. 외부 소스 + DB에서 컨텍스트 수집
# 2. 이전 대화 히스토리 주입 (선택)
# 3. 프롬프트 구성 후 LLM 호출
# ============================================================

def run_agent(query: str, history: list[str] | None = None) -> str:
    # 1. 컨텍스트 수집
    news = get_external_news(query)
    stock_data = get_db_stock_data(query)

    context = "\n".join([
        "=== 최신 뉴스 ===",
        *news,
        "\n=== DB 주가/재무 데이터 ===",
        *stock_data,
    ])

    # 2. 이전 대화 히스토리 구성
    history_text = ""
    if history:
        history_text = "\n=== 이전 대화 ===\n" + "\n".join(history)

    # 3. 프롬프트 구성 후 LLM 호출
    prompt = f"""당신은 금융 분석 AI입니다. 아래 수집된 정보를 바탕으로 사용자 질문에 답하세요.

{context}
{history_text}

사용자 질문: {query}
답변:"""

    return call_gemini(prompt)
