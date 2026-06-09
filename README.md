# FinBridge GraphRAG

주식·금융 데이터를 수집·분석·저장하고, 문서 검색·SQL 조회·지식그래프 탐색을 결합해 **근거 기반 금융 리서치 질의응답**을 제공하는 AI 백엔드 시스템입니다.

> 투자 추천, 매수·매도 신호 자동 제시, 실거래 연동은 제공하지 않습니다.

## 주요 기능

| 단계 | 기능 |
|------|------|
| MVP | yfinance 기반 주가 수집 → Kafka 스트리밍 → Spark 배치 분석 → 알림 생성 → FastAPI 조회 → Streamlit 대시보드 |
| 확장 | 뉴스/Reddit 수집 → 감성분석 → 공시/보고서 Vector RAG |
| 최종 | Neo4j GraphRAG + Text-to-SQL 통합 질의응답 |

## 아키텍처

```
[수집] yfinance / News API / Reddit
       ↓
[스트리밍] Kafka (stock-prices, raw-data topics)
       ↓
[배치 분석] Apache Spark (등락률, 거래량, 변동성)
       ↓
[저장] PostgreSQL (정형) / VectorDB (임베딩) / Neo4j (그래프)
       ↓
[AI 백엔드] FastAPI — Vector RAG + GraphRAG + Text-to-SQL
       ↓
[UI] Streamlit 대시보드 / Swagger
```

## 기술 스택

| 영역 | 기술 |
|------|------|
| 데이터 수집 | yfinance, News API, Reddit API |
| 스트리밍 | Apache Kafka |
| 배치 분석 | Apache Spark |
| 워크플로 | Apache Airflow |
| 정형 DB | PostgreSQL |
| 그래프 DB | Neo4j |
| Vector DB | (pgvector / Qdrant 선택) |
| 백엔드 | FastAPI, SQLAlchemy |
| AI | LangChain, OpenAI / Claude |
| UI | Streamlit |
| 테스트 | pytest, httpx |
| 인프라 | Docker Compose |

## 브랜치 전략

GitHub Flow 기반으로 운영합니다. 자세한 규칙은 [.github/BRANCH_STRATEGY.md](.github/BRANCH_STRATEGY.md)를 참고하세요.

```
feature/* → develop → main (릴리즈 태그)
```

| 브랜치    | 역할                        | force push |
|-----------|-----------------------------|-----------|
| `main`    | 프로덕션 릴리즈, 버전 태그  | 금지       |
| `develop` | 기능 통합 및 검증           | 금지       |
| `feature/*` | 개발 작업 단위            | 허용       |
