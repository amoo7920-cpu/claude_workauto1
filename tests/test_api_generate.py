from api.generate import MAX_LIMIT, build_response
from google_trends_agent.trends_fetcher import TrendTopic


def test_build_response_clamps_limit_and_includes_articles(monkeypatch):
    topics = [TrendTopic(title=f"검색어 {i}", approx_traffic="1000+") for i in range(5)]

    def fake_fetch(geo, limit):
        assert geo == "KR"
        assert limit == MAX_LIMIT  # 요청값(5)이 MAX_LIMIT(3)으로 클램프되어야 한다.
        return topics[:limit]

    def fake_write_article(topic, **kwargs):
        return f"{topic.title} 기사 본문"

    monkeypatch.setattr("api.generate.fetch_trending_topics", fake_fetch)
    monkeypatch.setattr("api.generate.write_article", fake_write_article)

    result = build_response("KR", 5)

    assert result["geo"] == "KR"
    assert result["count"] == MAX_LIMIT
    assert len(result["results"]) == MAX_LIMIT
    assert result["results"][0]["article"] == "검색어 0 기사 본문"


def test_build_response_continues_when_one_article_fails(monkeypatch):
    topics = [TrendTopic(title="정상 검색어"), TrendTopic(title="실패 검색어")]

    monkeypatch.setattr("api.generate.fetch_trending_topics", lambda geo, limit: topics[:limit])

    def fake_write_article(topic, **kwargs):
        if topic.title == "실패 검색어":
            raise RuntimeError("API 오류")
        return "정상 기사"

    monkeypatch.setattr("api.generate.write_article", fake_write_article)

    result = build_response("KR", 2)

    assert result["count"] == 2
    assert result["results"][0]["article"] == "정상 기사"
    assert "기사 생성 실패" in result["results"][1]["article"]
