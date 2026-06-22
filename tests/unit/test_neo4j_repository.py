import pytest
from unittest.mock import patch, MagicMock
from app.repositories.graph_db.neo4j_repository import Neo4jRepository

@patch("app.repositories.graph_db.neo4j_repository.run_cypher_query")
def test_upsert_company(mock_run_query):
    # Given
    repo = Neo4jRepository()
    symbol = "005930"
    name = "삼성전자"
    market = "KOSPI"
    industry = "반도체"

    # When
    repo.upsert_company(symbol, name, market, industry)

    # Then
    mock_run_query.assert_called_once()
    args, kwargs = mock_run_query.call_args
    query = args[0]
    params = args[1]
    
    assert "MERGE (c:Company {symbol: $symbol})" in query
    assert params["symbol"] == symbol
    assert params["name"] == name
    assert params["market"] == market
    assert params["industry"] == industry

@patch("app.repositories.graph_db.neo4j_repository.run_cypher_query")
def test_upsert_news(mock_run_query):
    # Given
    repo = Neo4jRepository()
    news_id = 999
    title = "Test News Title"
    source = "Test Source"
    url = "http://test.com"
    published_at = "2026-06-22T00:00:00Z"
    sentiment_score = 0.5
    sentiment_label = "positive"

    # When
    repo.upsert_news(
        news_id=news_id,
        title=title,
        source=source,
        url=url,
        published_at=published_at,
        sentiment_score=sentiment_score,
        sentiment_label=sentiment_label
    )

    # Then
    mock_run_query.assert_called_once()
    args, kwargs = mock_run_query.call_args
    params = args[1]
    
    assert params["id"] == news_id
    assert params["title"] == title
    assert params["sentiment_score"] == sentiment_score
    assert params["sentiment_label"] == sentiment_label

@patch("app.repositories.graph_db.neo4j_repository.run_cypher_query")
def test_get_company_network_not_found(mock_run_query):
    # Given
    repo = Neo4jRepository()
    # Company가 없을 때 빈 결과 반환해야 함
    mock_run_query.return_value = []

    # When
    result = repo.get_company_network("UNKNOWN")

    # Then
    assert result == {}
    mock_run_query.assert_called_once()

@patch("app.repositories.graph_db.neo4j_repository.run_cypher_query")
def test_get_company_network_success(mock_run_query):
    # Given
    repo = Neo4jRepository()
    
    # 순차적으로 run_cypher_query가 모의 결과를 반환하도록 설정
    # 1. Company 기본 정보
    # 2. 관련 뉴스 정보
    # 3. 직접 연결된 주제(Topic)
    # 4. 관련 이벤트 및 간접 주제
    mock_company = {"symbol": "005930", "name": "삼성전자", "market": "KOSPI", "industry": "반도체"}
    mock_news = [
        {
            "n": {"id": 101, "title": "삼성전자 영업이익 상승", "source": "SourceA", "url": "urlA", "published_at": "2026-06-22", "sentiment_score": 0.8, "sentiment_label": "positive"},
            "relevance_score": 0.95
        }
    ]
    mock_topics = [{"topic_name": "반도체", "weight": 0.8}]
    mock_events = [
        {
            "e": {"id": 201, "event_type": "금리변동", "description": "금리 동결", "event_date": "2026-06-12"},
            "impact_label": "neutral",
            "topics": ["금리", "거시경제"]
        }
    ]

    mock_run_query.side_effect = [
        [{"c": mock_company}],
        mock_news,
        mock_topics,
        mock_events
    ]

    # When
    network = repo.get_company_network("005930")

    # Then
    assert mock_run_query.call_count == 4
    assert network["company"]["symbol"] == "005930"
    assert len(network["news"]) == 1
    assert network["news"][0]["title"] == "삼성전자 영업이익 상승"
    assert len(network["topics"]) == 1
    assert network["topics"][0]["topic"] == "반도체"
    assert len(network["events"]) == 1
    assert network["events"][0]["event_type"] == "금리변동"
