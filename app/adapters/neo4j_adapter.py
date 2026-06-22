# ============================================================
# [Adapter Layer] Neo4j SDK 격리 영역
# ============================================================

import os
from typing import Any
from neo4j import GraphDatabase, Driver, Session
from neo4j.exceptions import Neo4jError

# 글로벌 드라이버 싱글톤
_driver: Driver | None = None

def init_neo4j_driver() -> Driver:
    """
    환경 변수를 기반으로 Neo4j 드라이버 인스턴스를 초기화하고 반환합니다.
    """
    global _driver
    if _driver is not None:
        return _driver

    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    username = os.getenv("NEO4J_USERNAME", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")

    try:
        _driver = GraphDatabase.driver(uri, auth=(username, password))
        # 연결성 확인을 위한 기본 테스트
        _driver.verify_connectivity()
        return _driver
    except Neo4jError as e:
        raise RuntimeError(f"Neo4j 드라이버 초기화 및 연결 검증 실패: {e}")
    except Exception as e:
        raise RuntimeError(f"Neo4j 연결 오류: {e}")

def get_neo4j_driver() -> Driver:
    """
    Neo4j 드라이버 싱글톤 인스턴스를 반환합니다. 초기화되지 않은 경우 초기화합니다.
    """
    global _driver
    if _driver is None:
        return init_neo4j_driver()
    return _driver

def close_neo4j_driver() -> None:
    """
    Neo4j 드라이버 커넥션 풀을 정상적으로 해제합니다.
    """
    global _driver
    if _driver is not None:
        try:
            _driver.close()
        except Exception as e:
            # 커넥션 종료 실패 시 로깅하거나 캐치
            pass
        finally:
            _driver = None

def run_cypher_query(query: str, parameters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """
    Cypher 쿼리를 실행하고 결과를 dict 리스트 형태로 변환하여 반환합니다.
    외부 SDK 예외를 내부적인 RuntimeError 등으로 감싸 반환합니다.
    """
    driver = get_neo4j_driver()
    params = parameters or {}
    
    try:
        with driver.session() as session:
            result = session.run(query, params)
            # 데이터를 직관적인 dictionary 리스트 형태로 로드
            return [dict(record) for record in result]
    except Neo4jError as e:
        raise RuntimeError(f"Neo4j Cypher 실행 중 데이터베이스 에러 발생 (Query: {query}): {e}")
    except Exception as e:
        raise RuntimeError(f"Neo4j 통신 오류 (Query: {query}): {e}")
