import sys
import os
from pathlib import Path

# 프로젝트 루트 경로를 sys.path에 추가 (app 모듈 import용)
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from app.repositories.graph_db.neo4j_repository import Neo4jRepository
from app.adapters.neo4j_adapter import close_neo4j_driver

# .env 로드
load_dotenv()

def seed_graph_data() -> None:
    """
    Neo4j 그래프 데이터베이스에 초기 테스트용 금융 온톨로지 샘플 데이터를 적재합니다.
    """
    print("Neo4j 초기 샘플 데이터 적재 시작...")
    repo = Neo4jRepository()

    # 1. 기업(Company) 적재
    companies = [
        {"symbol": "005930", "name": "삼성전자", "market": "KOSPI", "industry": "반도체"},
        {"symbol": "000660", "name": "SK하이닉스", "market": "KOSPI", "industry": "반도체"},
        {"symbol": "005380", "name": "현대자동차", "market": "KOSPI", "industry": "자동차제조업"},
        {"symbol": "TSLA", "name": "Tesla", "market": "NASDAQ", "industry": "자동차제조업"},
    ]
    print("[1] 기업 노드 생성 중...")
    for c in companies:
        repo.upsert_company(c["symbol"], c["name"], c["market"], c["industry"])
        print(f" - 기업 생성: {c['name']} ({c['symbol']})")

    # 2. 주제(Topic) 생성
    topics = ["반도체", "인공지능", "자율주행", "전기차", "거시경제", "금리"]
    print("\n[2] 주제 노드 생성 중...")
    for t in topics:
        repo.upsert_topic(t)
        print(f" - 주제 생성: {t}")

    # 3. 기업 ➔ 주제 관계(RELATED_TO) 적재
    company_topics = [
        {"symbol": "005930", "topic": "반도체", "weight": 0.8},
        {"symbol": "005930", "topic": "인공지능", "weight": 0.4},
        {"symbol": "000660", "topic": "반도체", "weight": 0.9},
        {"symbol": "000660", "topic": "인공지능", "weight": 0.7},
        {"symbol": "005380", "topic": "자율주행", "weight": 0.5},
        {"symbol": "005380", "topic": "전기차", "weight": 0.6},
        {"symbol": "TSLA", "topic": "전기차", "weight": 0.8},
        {"symbol": "TSLA", "topic": "자율주행", "weight": 0.7},
    ]
    print("\n[3] 기업-주제 관계 설정 중...")
    for ct in company_topics:
        repo.add_company_related_to_topic(ct["symbol"], ct["topic"], ct["weight"])
        print(f" - 관계 설정: {ct['symbol']} -[RELATED_TO]-> {ct['topic']} (가중치: {ct['weight']})")

    # 4. 뉴스(News) 적재
    news_items = [
        {
            "id": 101,
            "title": "삼성전자 2분기 영업이익 10조 돌파 전망 - 반도체 수요 회복 신호",
            "source": "한국경제",
            "url": "https://www.hankyung.com/finance/101",
            "published_at": "2026-06-14T09:00:00Z",
            "sentiment_score": 0.85,
            "sentiment_label": "positive"
        },
        {
            "id": 102,
            "title": "SK하이닉스, 차세대 HBM 공급 계약 체결 - 인공지능 서버 수요 급증",
            "source": "매일경제",
            "url": "https://www.mk.co.kr/news/102",
            "published_at": "2026-06-15T10:30:00Z",
            "sentiment_score": 0.92,
            "sentiment_label": "positive"
        },
        {
            "id": 103,
            "title": "테슬라, 자율주행 FSD 라이선스 파트너십 논의 본격화",
            "source": "Reuters",
            "url": "https://www.reuters.com/tsla/103",
            "published_at": "2026-06-15T15:00:00Z",
            "sentiment_score": 0.78,
            "sentiment_label": "positive"
        },
        {
            "id": 104,
            "title": "Fed, 6월 기준금리 동결 결정 - 금리 고공행진 장기화 우려",
            "source": "연합인포맥스",
            "url": "https://news.einfomax.co.kr/104",
            "published_at": "2026-06-12T22:00:00Z",
            "sentiment_score": -0.45,
            "sentiment_label": "negative"
        }
    ]
    print("\n[4] 뉴스 노드 생성 중...")
    for n in news_items:
        repo.upsert_news(
            n["id"], n["title"], n["source"], n["url"], 
            n["published_at"], n["sentiment_score"], n["sentiment_label"]
        )
        print(f" - 뉴스 생성: ID {n['id']} - {n['title'][:20]}...")

    # 5. 기업 ➔ 뉴스 언급 관계(MENTIONED_IN) 적재
    mentions = [
        {"symbol": "005930", "news_id": 101, "relevance_score": 0.95},
        {"symbol": "000660", "news_id": 102, "relevance_score": 0.92},
        {"symbol": "TSLA", "news_id": 103, "relevance_score": 0.88},
    ]
    print("\n[5] 기업-뉴스 언급 관계 설정 중...")
    for m in mentions:
        repo.add_company_mentioned_in_news(m["symbol"], m["news_id"], m["relevance_score"])
        print(f" - 관계 설정: {m['symbol']} -[MENTIONED_IN]-> 뉴스 ID {m['news_id']}")

    # 6. 뉴스 ➔ 주제 관계(RELATED_TO) 적재
    news_topics = [
        {"news_id": 101, "topic": "반도체"},
        {"news_id": 102, "topic": "반도체"},
        {"news_id": 102, "topic": "인공지능"},
        {"news_id": 103, "topic": "자율주행"},
        {"news_id": 103, "topic": "전기차"},
        {"news_id": 104, "topic": "거시경제"},
        {"news_id": 104, "topic": "금리"},
    ]
    print("\n[6] 뉴스-주제 관계 설정 중...")
    for nt in news_topics:
        repo.add_news_related_to_topic(nt["news_id"], nt["topic"])
        print(f" - 관계 설정: 뉴스 ID {nt['news_id']} -[RELATED_TO]-> {nt['topic']}")

    # 7. 이벤트(Event) 적재
    events = [
        {
            "id": 201,
            "event_type": "금리변동",
            "description": "연준(Fed), 2026년 6월 연방공개시장위원회(FOMC)에서 기준금리를 현 5.25~5.50% 수준으로 만장일치 동결",
            "event_date": "2026-06-12"
        },
        {
            "id": 202,
            "event_type": "기술협력",
            "description": "글로벌 AI 칩 제조업체 엔비디아(NVIDIA), 차세대 HBM4 개발 프로젝트 파트너십 체결 완료 공식 발표",
            "event_date": "2026-06-15"
        }
    ]
    print("\n[7] 이벤트 노드 생성 중...")
    for e in events:
        repo.upsert_event(e["id"], e["event_type"], e["description"], e["event_date"])
        print(f" - 이벤트 생성: ID {e['id']} - {e['event_type']}")

    # 8. 기업 ➔ 이벤트 영향 관계(AFFECTED_BY) 적재
    company_events = [
        {"symbol": "005930", "event_id": 202, "impact": "positive"},
        {"symbol": "000660", "event_id": 202, "impact": "positive"},
        {"symbol": "TSLA", "event_id": 201, "impact": "neutral"},
    ]
    print("\n[8] 기업-이벤트 영향 관계 설정 중...")
    for ce in company_events:
        repo.add_company_affected_by_event(ce["symbol"], ce["event_id"], ce["impact"])
        print(f" - 관계 설정: {ce['symbol']} -[AFFECTED_BY]-> 이벤트 ID {ce['event_id']} ({ce['impact']})")

    # 9. 이벤트 ➔ 주제 영향 관계(INFLUENCED_BY) 적재
    event_topics = [
        {"event_id": 201, "topic": "금리"},
        {"event_id": 201, "topic": "거시경제"},
        {"event_id": 202, "topic": "반도체"},
        {"event_id": 202, "topic": "인공지능"},
    ]
    print("\n[9] 이벤트-주제 관계 설정 중...")
    for et in event_topics:
        repo.add_event_influenced_by_topic(et["event_id"], et["topic"])
        print(f" - 관계 설정: 이벤트 ID {et['event_id']} -[INFLUENCED_BY]-> {et['topic']}")

    print("\nNeo4j 초기 샘플 데이터 적재 완료!")

if __name__ == "__main__":
    try:
        seed_graph_data()
    finally:
        close_neo4j_driver()
