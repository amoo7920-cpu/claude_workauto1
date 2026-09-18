"""구글 트렌드(Google Trends) 실시간 인기 검색어 수집 모듈.

구글이 공개하는 'Trending Now' RSS 피드(https://trends.google.com/trending/rss)를
내려받아 각 인기 검색어와 함께 제공되는 연관 뉴스(제목/요약/출처/링크)까지 파싱한다.
연관 뉴스는 기사 작성 단계에서 '상세 정보'의 근거 자료로 사용된다.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Optional

import requests

RSS_URL = "https://trends.google.com/trending/rss"
DEFAULT_TIMEOUT = 15
# 기본 User-Agent 없이 요청하면 구글이 응답을 거부하는 경우가 있어 명시한다.
USER_AGENT = (
    "Mozilla/5.0 (compatible; GoogleTrendsAgent/1.0; "
    "+https://github.com/)"
)


@dataclass
class NewsItem:
    title: str = ""
    snippet: str = ""
    url: str = ""
    source: str = ""
    picture: str = ""


@dataclass
class TrendTopic:
    title: str = ""
    link: str = ""
    approx_traffic: str = ""
    pub_date: str = ""
    picture: str = ""
    picture_source: str = ""
    news_items: list[NewsItem] = field(default_factory=list)


def _local_tag(tag: str) -> str:
    """XML 네임스페이스 접두사를 제거하고 태그 이름만 반환한다."""
    return tag.split("}")[-1] if "}" in tag else tag


def _download_rss(geo: str) -> str:
    response = requests.get(
        RSS_URL,
        params={"geo": geo},
        headers={"User-Agent": USER_AGENT},
        timeout=DEFAULT_TIMEOUT,
    )
    response.raise_for_status()
    return response.text


def _parse_news_item(item_el: ET.Element) -> NewsItem:
    news = NewsItem()
    for child in item_el:
        tag = _local_tag(child.tag)
        text = (child.text or "").strip()
        if tag == "news_item_title":
            news.title = text
        elif tag == "news_item_snippet":
            news.snippet = text
        elif tag == "news_item_url":
            news.url = text
        elif tag == "news_item_source":
            news.source = text
        elif tag == "news_item_picture":
            news.picture = text
    return news


def _parse_topic(item_el: ET.Element) -> TrendTopic:
    topic = TrendTopic()
    for child in item_el:
        tag = _local_tag(child.tag)
        text = (child.text or "").strip()
        if tag == "title":
            topic.title = text
        elif tag == "link":
            topic.link = text
        elif tag == "pubDate":
            topic.pub_date = text
        elif tag == "approx_traffic":
            topic.approx_traffic = text
        elif tag == "picture":
            topic.picture = text
        elif tag == "picture_source":
            topic.picture_source = text
        elif tag == "news_item":
            topic.news_items.append(_parse_news_item(child))
    return topic


def parse_trending_rss(rss_text: str, limit: Optional[int] = None) -> list[TrendTopic]:
    """RSS 피드 원문(XML 문자열)을 TrendTopic 목록으로 변환한다."""
    root = ET.fromstring(rss_text)
    topics: list[TrendTopic] = []
    for item_el in root.iter():
        if _local_tag(item_el.tag) != "item":
            continue
        topics.append(_parse_topic(item_el))
        if limit is not None and len(topics) >= limit:
            break
    return topics


def fetch_trending_topics(
    geo: str = "KR",
    limit: int = 10,
    rss_text: Optional[str] = None,
) -> list[TrendTopic]:
    """구글 트렌드 인기 검색어를 조회한다.

    Args:
        geo: 국가 코드 (예: KR, US, JP).
        limit: 가져올 최대 검색어 개수.
        rss_text: 테스트용으로 RSS 원문을 직접 주입할 때 사용. None이면 실제로 다운로드한다.
    """
    if rss_text is None:
        rss_text = _download_rss(geo)
    return parse_trending_rss(rss_text, limit=limit)
