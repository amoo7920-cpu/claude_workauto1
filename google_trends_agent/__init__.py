"""구글 트렌드 인기 검색어를 조사하고 상세 기사를 작성하는 에이전트."""

from .trends_fetcher import TrendTopic, fetch_trending_topics
from .article_writer import write_article

__all__ = ["TrendTopic", "fetch_trending_topics", "write_article"]
