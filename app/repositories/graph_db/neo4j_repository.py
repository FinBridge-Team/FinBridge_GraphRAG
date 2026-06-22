# ============================================================
# [Repository Layer] Neo4j 지식그래프 조회 및 데이터 적재 영역
# ============================================================

from typing import Any
from app.adapters.neo4j_adapter import run_cypher_query

class Neo4jRepository:
    """
    Neo4j 그래프 데이터베이스의 노드/엣지 CRUD 및 복합 관계 순회 조회를 담당하는 리포지토리 클래스입니다.
    """

    def upsert_company(self, symbol: str, name: str, market: str | None = None, industry: str | None = None) -> None:
        """
        Company 노드를 생성하거나 업데이트(UPSERT)합니다.
        """
        query = """
        MERGE (c:Company {symbol: $symbol})
        ON CREATE SET c.name = $name, 
                      c.market = $market, 
                      c.industry = $industry, 
                      c.created_at = datetime()
        ON MATCH SET c.name = $name, 
                     c.market = COALESCE($market, c.market), 
                     c.industry = COALESCE($industry, c.industry)
        """
        run_cypher_query(query, {
            "symbol": symbol,
            "name": name,
            "market": market,
            "industry": industry
        })

    def upsert_news(
        self, 
        news_id: int, 
        title: str, 
        source: str | None = None, 
        url: str | None = None, 
        published_at: str | None = None,
        sentiment_score: float | None = None,
        sentiment_label: str | None = None
    ) -> None:
        """
        News 노드를 생성하거나 업데이트(UPSERT)합니다.
        """
        query = """
        MERGE (n:News {id: $id})
        ON CREATE SET n.title = $title, 
                      n.source = $source, 
                      n.url = $url, 
                      n.published_at = datetime($published_at),
                      n.sentiment_score = $sentiment_score,
                      n.sentiment_label = $sentiment_label
        ON MATCH SET n.title = $title,
                     n.source = COALESCE($source, n.source),
                     n.url = COALESCE($url, n.url),
                     n.published_at = COALESCE(datetime($published_at), n.published_at),
                     n.sentiment_score = COALESCE($sentiment_score, n.sentiment_score),
                     n.sentiment_label = COALESCE($sentiment_label, n.sentiment_label)
        """
        # ISO8601 포맷 파싱 및 대응
        run_cypher_query(query, {
            "id": news_id,
            "title": title,
            "source": source,
            "url": url,
            "published_at": published_at,
            "sentiment_score": sentiment_score,
            "sentiment_label": sentiment_label
        })

    def upsert_event(
        self, 
        event_id: int, 
        event_type: str | None = None, 
        description: str | None = None, 
        event_date: str | None = None
    ) -> None:
        """
        Event 노드를 생성하거나 업데이트(UPSERT)합니다.
        """
        query = """
        MERGE (e:Event {id: $id})
        ON CREATE SET e.event_type = $event_type, 
                      e.description = $description, 
                      e.event_date = date($event_date)
        ON MATCH SET e.event_type = COALESCE($event_type, e.event_type), 
                     e.description = COALESCE($description, e.description), 
                     e.event_date = COALESCE(date($event_date), e.event_date)
        """
        run_cypher_query(query, {
            "id": event_id,
            "event_type": event_type,
            "description": description,
            "event_date": event_date
        })

    def upsert_topic(self, name: str) -> None:
        """
        Topic 노드를 생성하거나 업데이트(UPSERT)합니다.
        """
        query = """
        MERGE (t:Topic {name: $name})
        """
        run_cypher_query(query, {"name": name})

    def add_company_mentioned_in_news(self, symbol: str, news_id: int, relevance_score: float | None = None) -> None:
        """
        Company 노드와 News 노드 간의 [:MENTIONED_IN] 관계를 생성합니다.
        """
        query = """
        MATCH (c:Company {symbol: $symbol})
        MATCH (n:News {id: $news_id})
        MERGE (c)-[r:MENTIONED_IN]->(n)
        ON CREATE SET r.relevance_score = $relevance_score
        ON MATCH SET r.relevance_score = COALESCE($relevance_score, r.relevance_score)
        """
        run_cypher_query(query, {
            "symbol": symbol,
            "news_id": news_id,
            "relevance_score": relevance_score
        })

    def add_news_related_to_topic(self, news_id: int, topic_name: str) -> None:
        """
        News 노드와 Topic 노드 간의 [:RELATED_TO] 관계를 생성합니다.
        """
        query = """
        MATCH (n:News {id: $news_id})
        MERGE (t:Topic {name: $topic_name})
        MERGE (n)-[:RELATED_TO]->(t)
        """
        run_cypher_query(query, {
            "news_id": news_id,
            "topic_name": topic_name
        })

    def add_company_related_to_topic(self, symbol: str, topic_name: str, weight: float | None = 1.0) -> None:
        """
        Company 노드와 Topic 노드 간의 [:RELATED_TO] 관계를 생성합니다.
        """
        query = """
        MATCH (c:Company {symbol: $symbol})
        MERGE (t:Topic {name: $topic_name})
        MERGE (c)-[r:RELATED_TO]->(t)
        ON CREATE SET r.weight = $weight
        ON MATCH SET r.weight = COALESCE($weight, r.weight)
        """
        run_cypher_query(query, {
            "symbol": symbol,
            "topic_name": topic_name,
            "weight": weight
        })

    def add_company_affected_by_event(self, symbol: str, event_id: int, impact_label: str | None = None) -> None:
        """
        Company 노드와 Event 노드 간의 [:AFFECTED_BY] 관계를 생성합니다.
        """
        query = """
        MATCH (c:Company {symbol: $symbol})
        MATCH (e:Event {id: $event_id})
        MERGE (c)-[r:AFFECTED_BY]->(e)
        ON CREATE SET r.impact_label = $impact_label
        ON MATCH SET r.impact_label = COALESCE($impact_label, r.impact_label)
        """
        run_cypher_query(query, {
            "symbol": symbol,
            "event_id": event_id,
            "impact_label": impact_label
        })

    def add_event_influenced_by_topic(self, event_id: int, topic_name: str) -> None:
        """
        Event 노드와 Topic 노드 간의 [:INFLUENCED_BY] 관계를 생성합니다.
        """
        query = """
        MATCH (e:Event {id: $event_id})
        MERGE (t:Topic {name: $topic_name})
        MERGE (e)-[:INFLUENCED_BY]->(t)
        """
        run_cypher_query(query, {
            "event_id": event_id,
            "topic_name": topic_name
        })

    def get_company_network(self, symbol: str, limit: int = 10) -> dict[str, Any]:
        """
        특정 기업에 연결된 주변 네트워크(뉴스, 관련 주제, 이벤트 등)를 1-hop~2-hop 범위 내에서 조회하여
        GraphRAG 프롬프트에 활용 가능한 구조화된 컨텍스트 데이터를 반환합니다.
        """
        # 1. Company 기본 정보 가져오기
        company_query = "MATCH (c:Company {symbol: $symbol}) RETURN c"
        company_res = run_cypher_query(company_query, {"symbol": symbol})
        if not company_res:
            return {}
        
        company = company_res[0]["c"]

        # 2. 관련 뉴스 정보 조회
        news_query = """
        MATCH (c:Company {symbol: $symbol})-[r:MENTIONED_IN]->(n:News)
        RETURN n, r.relevance_score as relevance_score
        ORDER BY n.published_at DESC LIMIT $limit
        """
        news_res = run_cypher_query(news_query, {"symbol": symbol, "limit": limit})
        news_list = []
        for row in news_res:
            n = row["n"]
            news_list.append({
                "id": n.get("id"),
                "title": n.get("title"),
                "source": n.get("source"),
                "url": n.get("url"),
                "published_at": str(n.get("published_at")),
                "sentiment_score": n.get("sentiment_score"),
                "sentiment_label": n.get("sentiment_label"),
                "relevance_score": row["relevance_score"]
            })

        # 3. 직접 연결된 주제(Topic) 조회
        topic_query = """
        MATCH (c:Company {symbol: $symbol})-[r:RELATED_TO]->(t:Topic)
        RETURN t.name as topic_name, r.weight as weight
        """
        topic_res = run_cypher_query(topic_query, {"symbol": symbol})
        topic_list = [{"topic": row["topic_name"], "weight": row["weight"]} for row in topic_res]

        # 4. 관련 이벤트 및 간접 주제(이벤트 ➔ 주제) 조회
        event_query = """
        MATCH (c:Company {symbol: $symbol})-[r:AFFECTED_BY]->(e:Event)
        OPTIONAL MATCH (e)-[:INFLUENCED_BY]->(t:Topic)
        RETURN e, r.impact_label as impact_label, collect(t.name) as topics
        ORDER BY e.event_date DESC LIMIT $limit
        """
        event_res = run_cypher_query(event_query, {"symbol": symbol, "limit": limit})
        event_list = []
        for row in event_res:
            e = row["e"]
            event_list.append({
                "id": e.get("id"),
                "event_type": e.get("event_type"),
                "description": e.get("description"),
                "event_date": str(e.get("event_date")),
                "impact_label": row["impact_label"],
                "related_topics": row["topics"]
            })

        return {
            "company": {
                "symbol": company.get("symbol"),
                "name": company.get("name"),
                "market": company.get("market"),
                "industry": company.get("industry")
            },
            "news": news_list,
            "topics": topic_list,
            "events": event_list
        }
