from google_trends_agent.trends_fetcher import parse_trending_rss

SAMPLE_RSS = """<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0" xmlns:ht="https://trends.google.com/trends/trendingsearches/daily">
<channel>
<title>Daily Search Trends</title>
<item>
  <title>예시 검색어 A</title>
  <ht:approx_traffic>50000+</ht:approx_traffic>
  <description>예시 검색어 A</description>
  <link>https://trends.google.com/trends/explore?q=%EC%98%88%EC%8B%9C</link>
  <pubDate>Thu, 18 Sep 2026 09:00:00 -0000</pubDate>
  <ht:picture>https://example.com/a.jpg</ht:picture>
  <ht:picture_source>예시 언론사</ht:picture_source>
  <ht:news_item>
    <ht:news_item_title>예시 검색어 A 관련 뉴스 1</ht:news_item_title>
    <ht:news_item_snippet>뉴스 요약 내용입니다.</ht:news_item_snippet>
    <ht:news_item_url>https://news.example.com/1</ht:news_item_url>
    <ht:news_item_picture>https://example.com/n1.jpg</ht:news_item_picture>
    <ht:news_item_source>뉴스사 1</ht:news_item_source>
  </ht:news_item>
  <ht:news_item>
    <ht:news_item_title>예시 검색어 A 관련 뉴스 2</ht:news_item_title>
    <ht:news_item_snippet>두번째 뉴스 요약입니다.</ht:news_item_snippet>
    <ht:news_item_url>https://news.example.com/2</ht:news_item_url>
    <ht:news_item_source>뉴스사 2</ht:news_item_source>
  </ht:news_item>
</item>
<item>
  <title>예시 검색어 B</title>
  <ht:approx_traffic>10000+</ht:approx_traffic>
  <link>https://trends.google.com/trends/explore?q=B</link>
  <pubDate>Thu, 18 Sep 2026 08:00:00 -0000</pubDate>
</item>
</channel>
</rss>
"""


def test_parse_trending_rss_extracts_topics_and_news():
    topics = parse_trending_rss(SAMPLE_RSS)

    assert len(topics) == 2

    first = topics[0]
    assert first.title == "예시 검색어 A"
    assert first.approx_traffic == "50000+"
    assert first.picture_source == "예시 언론사"
    assert len(first.news_items) == 2
    assert first.news_items[0].title == "예시 검색어 A 관련 뉴스 1"
    assert first.news_items[0].source == "뉴스사 1"
    assert first.news_items[0].url == "https://news.example.com/1"

    second = topics[1]
    assert second.title == "예시 검색어 B"
    assert second.news_items == []


def test_parse_trending_rss_respects_limit():
    topics = parse_trending_rss(SAMPLE_RSS, limit=1)
    assert len(topics) == 1
    assert topics[0].title == "예시 검색어 A"
