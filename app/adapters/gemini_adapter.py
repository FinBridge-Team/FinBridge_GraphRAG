import os
from google import genai

# ============================================================
# [Adapter Layer] Gemini SDK 격리 영역
# ============================================================

def call_gemini(prompt: str, model: str = "gemini-2.5-flash-lite") -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다.")

    client = genai.Client(api_key=api_key)
    try:
        response = client.models.generate_content(model=model, contents=prompt)
        return response.text
    except Exception as e:
        raise RuntimeError(f"Gemini 통신 오류: {e}")
