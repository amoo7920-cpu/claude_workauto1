from google_trends_agent.article_writer import build_user_prompt, write_article
from google_trends_agent.trends_fetcher import NewsItem, TrendTopic


def test_build_user_prompt_includes_trend_and_news_details():
    topic = TrendTopic(
        title="예시 검색어",
        approx_traffic="20000+",
        pub_date="Thu, 18 Sep 2026 09:00:00 -0000",
        link="https://trends.google.com/trends/explore?q=example",
        news_items=[
            NewsItem(
                title="관련 뉴스 제목",
                snippet="뉴스 요약",
                url="https://news.example.com/1",
                source="예시 뉴스사",
            )
        ],
    )

    prompt = build_user_prompt(topic)

    assert "예시 검색어" in prompt
    assert "20000+" in prompt
    assert "관련 뉴스 제목" in prompt
    assert "예시 뉴스사" in prompt
    assert "https://news.example.com/1" in prompt


class _FakeTextBlock:
    def __init__(self, text: str):
        self.type = "text"
        self.text = text


class _FakeResponse:
    def __init__(self, text: str):
        self.content = [_FakeTextBlock(text)]


class _FakeMessages:
    def __init__(self, expected_text: str):
        self._expected_text = expected_text
        self.last_call = None

    def create(self, **kwargs):
        self.last_call = kwargs
        return _FakeResponse(self._expected_text)


class _FakeClient:
    def __init__(self, expected_text: str):
        self.messages = _FakeMessages(expected_text)


def test_write_article_uses_injected_client_and_returns_text():
    topic = TrendTopic(title="예시 검색어")
    fake_client = _FakeClient("생성된 기사 본문")

    result = write_article(topic, model="claude-sonnet-5", client=fake_client)

    assert result == "생성된 기사 본문"
    assert fake_client.messages.last_call["model"] == "claude-sonnet-5"
    assert "예시 검색어" in fake_client.messages.last_call["messages"][0]["content"]
