import sys
import os
from pathlib import Path

# 프로젝트 루트 경로를 sys.path에 추가 (app 모듈 import용)
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from app.adapters.neo4j_adapter import run_cypher_query, close_neo4j_driver

# .env 로드
load_dotenv()

def init_neo4j_schema() -> None:
    """
    Neo4j 그래프 데이터베이스의 온톨로지 제약 조건(Constraints) 및 인덱스(Indexes)를 설정합니다.
    """
    print("Neo4j 스키마 초기화 시작...")

    # Neo4j 5.x 문법을 준수합니다.
    constraints = [
        ("Company_symbol_unique", "CREATE CONSTRAINT Company_symbol_unique IF NOT EXISTS FOR (c:Company) REQUIRE c.symbol IS UNIQUE"),
        ("News_id_unique", "CREATE CONSTRAINT News_id_unique IF NOT EXISTS FOR (n:News) REQUIRE n.id IS UNIQUE"),
        ("Event_id_unique", "CREATE CONSTRAINT Event_id_unique IF NOT EXISTS FOR (e:Event) REQUIRE e.id IS UNIQUE"),
        ("Topic_name_unique", "CREATE CONSTRAINT Topic_name_unique IF NOT EXISTS FOR (t:Topic) REQUIRE t.name IS UNIQUE"),
    ]

    indexes = [
        ("Company_name_idx", "CREATE INDEX Company_name_idx IF NOT EXISTS FOR (c:Company) ON (c.name)"),
        ("News_published_at_idx", "CREATE INDEX News_published_at_idx IF NOT EXISTS FOR (n:News) ON (n.published_at)"),
        ("Event_event_date_idx", "CREATE INDEX Event_event_date_idx IF NOT EXISTS FOR (e:Event) ON (e.event_date)"),
    ]

    print("\n[1] 고유 제약 조건(Constraints) 생성:")
    for name, query in constraints:
        try:
            run_cypher_query(query)
            print(f" - {name} 제약 조건 설정 성공")
        except Exception as e:
            print(f" - {name} 제약 조건 설정 실패: {e}")

    print("\n[2] 인덱스(Indexes) 생성:")
    for name, query in indexes:
        try:
            run_cypher_query(query)
            print(f" - {name} 인덱스 설정 성공")
        except Exception as e:
            print(f" - {name} 인덱스 설정 실패: {e}")

    print("\nNeo4j 스키마 초기화 완료!")

if __name__ == "__main__":
    try:
        init_neo4j_schema()
    finally:
        close_neo4j_driver()
