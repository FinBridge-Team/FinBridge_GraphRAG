# FinBridge GraphRAG — Python 개발 컨벤션

---

## 1. 레이어 아키텍처 (필수 준수)

```
app/
├── adapters/      ← [Adapter Layer]   외부 SDK / DB 기술 격리
├── services/      ← [Service Layer]   비즈니스 로직 / 오케스트레이션
├── apis/
│   ├── dtos/      ← [DTO Layer]       Request / Response 모델
│   └── *_router   ← [API Layer]       FastAPI 라우팅
└── main.py        ← 앱 진입점, 라우터 등록
```

**의존 방향은 단방향입니다. 역방향 import 금지:**

```
API Layer → Service Layer → Adapter Layer
```

---

## 2. 파일 네이밍

| 대상 | 규칙 | 예시 |
|---|---|---|
| 파일명 | `snake_case` + 역할 suffix | `gemini_adapter.py`, `chat_service.py`, `agent_router.py` |
| DTO 파일 | 도메인명 + `_dto` | `chat_dto.py`, `agent_dto.py` |
| 라우터 변수 | import 시 alias 필수 | `from ... import router as chat_router` |

---

## 3. 클래스 / 함수 네이밍

```python
# 클래스: PascalCase
class ChatRequest(BaseModel): ...
class AgentResponse(BaseModel): ...

# 함수: 동사_목적어, snake_case
def call_gemini(...)        # Adapter: 기술 동작
def get_external_news(...)  # Adapter: 데이터 수집
def process_chat(...)       # Service: 비즈니스 처리
def run_agent(...)          # Service: 오케스트레이션
```

---

## 4. 타입 힌트 — 전 레이어 필수

```python
# 파라미터 + 반환값 모두 명시
def call_gemini(prompt: str, model: str = "gemini-2.5-flash-lite") -> str: ...
def get_external_news(query: str) -> list[str]: ...
def run_agent(query: str) -> str: ...

# Optional 파라미터는 | None 문법 사용 (Python 3.10+)
def run_agent(query: str, history: list[str] | None = None) -> str: ...
```

---

## 5. 레이어별 파일 헤더 (필수)

```python
# ============================================================
# [Adapter Layer] Gemini SDK 격리 영역
# ============================================================

# ============================================================
# [Service Layer] Agent 오케스트레이션 영역
# ============================================================

# ============================================================
# [API Layer] 라우팅 영역
# ============================================================
```

---

## 6. Adapter 작성 규칙

```python
# ✅ 올바른 패턴 — SDK/기술을 함수 내부로 격리
def call_gemini(prompt: str) -> str:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    ...

# ❌ 금지 — Service/Router에서 SDK 직접 호출
def run_agent(query: str) -> str:
    client = genai.Client(...)   # 레이어 위반
```

- 예외는 `raise`로 상위로 전파 (`ValueError`, `RuntimeError`)
- Mock 어댑터는 실제 교체 대상 명시

```python
# 실제 구현 시 yfinance, NewsAPI, PostgreSQL, Neo4j 등으로 교체
def get_external_news(query: str) -> list[str]:
    ...
```

---

## 7. DTO 작성 규칙

```python
from pydantic import BaseModel

class AgentRequest(BaseModel):   # 입력: Request suffix
    query: str

class AgentResponse(BaseModel):  # 출력: Response suffix
    query: str
    answer: str
```

- `BaseModel` 상속 필수
- 필드는 **단수 명사**, snake_case
- DTO는 라우터와 서비스 사이 경계에서만 사용
- 세션 기반 엔드포인트는 `session_id` 필드 포함

```python
class ChatRequest(BaseModel):
    session_id: str   # 대화 세션 식별자
    message: str
```

---

## 8. Router 작성 규칙

```python
router = APIRouter(prefix="/agent", tags=["agent"])

@router.post("/query", response_model=AgentResponse)
async def query(request: AgentRequest) -> AgentResponse:
    answer = run_agent(request.query)
    return AgentResponse(query=request.query, answer=answer)
```

- 모든 핸들러는 `async def`
- `response_model` + 반환 타입 힌트 이중 명시
- 비즈니스 로직은 서비스로 위임, 라우터는 얇게 유지

---

## 9. 환경변수

```python
# main.py 최상단에서 1회만 로드
load_dotenv()

# Adapter 내부에서 os.getenv() 사용
api_key = os.getenv("GEMINI_API_KEY")
```

---

## 11. 인메모리 상태 관리 (샘플 패턴)

세션 히스토리 등 임시 상태는 Service 레이어 모듈 변수로 관리합니다.

```python
# 모듈 상단에 선언 — 서버 생애주기와 동일
_history: dict[str, list[str]] = {}

def process_chat(session_id: str, message: str) -> str:
    history = _history.get(session_id, [])
    answer = run_agent(message, history)
    history.append(f"사용자: {message}")
    history.append(f"AI: {answer}")
    _history[session_id] = history[-10:]  # 최근 5턴 유지
    return answer
```

| 항목 | 샘플 (현재) | 실제 운영 |
|---|---|---|
| 저장소 | 모듈 변수 `dict` | Redis / PostgreSQL |
| 서버 재시작 | 히스토리 초기화 | 영속 유지 |
| 멀티 프로세스 | 공유 불가 | 공유 가능 |

---

## 10. import 순서

```python
# 1. 표준 라이브러리
import os

# 2. 서드파티
from fastapi import APIRouter
from pydantic import BaseModel

# 3. 로컬 (app.* 경로)
from app.services.agent_service import run_agent
```
