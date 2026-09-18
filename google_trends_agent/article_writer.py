"""수집된 트렌드 정보를 바탕으로 Claude가 상세 기사를 작성하는 모듈."""

from __future__ import annotations

import os
from typing import Optional

from .trends_fetcher import TrendTopic

DEFAULT_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")

SYSTEM_PROMPT = """\
당신은 실시간 이슈를 알기 쉽게 풀어 쓰는 한국어 온라인 매체의 기자입니다.
주어진 '구글 트렌드 인기 검색어'와 '관련 뉴스 요약'만을 근거로,
정확하고 균형 잡힌 상세 기사를 작성하세요.

작성 규칙:
- 확인되지 않은 사실을 단정적으로 지어내지 말고, 제공된 근거 안에서만 서술하세요.
- 근거가 부족한 부분은 "정확한 배경은 추가 확인이 필요하다" 등으로 명시하세요.
- 다음 구조의 마크다운으로 작성하세요.
  1. 제목 (# )
  2. 한 줄 요약 (굵게)
  3. 지금 왜 화제인가 (검색량, 시점 등 트렌드 정보 반영)
  4. 상세 배경 및 관련 뉴스 정리 (출처 명시)
  5. 마무리 / 시사점
- 전체 분량은 800~1200자 내외의 한국어로 작성하세요.
"""


def build_user_prompt(topic: TrendTopic) -> str:
    lines = [f"## 트렌드 키워드: {topic.title}"]
    if topic.approx_traffic:
        lines.append(f"- 추정 검색량: {topic.approx_traffic}")
    if topic.pub_date:
        lines.append(f"- 트렌드 집계 시각: {topic.pub_date}")
    if topic.link:
        lines.append(f"- 구글 트렌드 링크: {topic.link}")

    if topic.news_items:
        lines.append("\n### 관련 뉴스")
        for idx, news in enumerate(topic.news_items, 1):
            lines.append(f"{idx}. [{news.source or '출처 미상'}] {news.title}")
            if news.snippet:
                lines.append(f"   - 요약: {news.snippet}")
            if news.url:
                lines.append(f"   - 링크: {news.url}")
    else:
        lines.append("\n(연관 뉴스 정보가 제공되지 않았습니다. 검색어 자체의 맥락을 바탕으로 작성하세요.)")

    lines.append("\n위 정보를 근거로 상세 기사를 작성해 주세요.")
    return "\n".join(lines)


def write_article(
    topic: TrendTopic,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 2000,
    client: Optional[object] = None,
) -> str:
    """Anthropic API를 호출해 트렌드 주제에 대한 상세 기사를 생성한다."""
    if client is None:
        from anthropic import Anthropic

        client = Anthropic()

    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_user_prompt(topic)}],
    )
    return "".join(
        block.text for block in response.content if getattr(block, "type", None) == "text"
    )
