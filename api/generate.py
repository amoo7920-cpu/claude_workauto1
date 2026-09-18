"""Vercel Python 서버리스 함수: 구글 트렌드 상세 기사 API.

GET /api/generate?geo=KR&limit=2
  - geo: 국가 코드 (기본값 KR)
  - limit: 가져올 트렌드 개수 (1~2, 서버리스 함수 기본 실행 시간 제한 때문에 최대 2로 제한)
"""

from __future__ import annotations

import json
import os
import sys
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Vercel 런타임에서 저장소 루트의 google_trends_agent 패키지를 임포트할 수 있도록 경로를 추가한다.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google_trends_agent.article_writer import write_article  # noqa: E402
from google_trends_agent.trends_fetcher import TrendTopic, fetch_trending_topics  # noqa: E402

MAX_LIMIT = 2


def _topic_to_dict(topic: TrendTopic, article: str) -> dict:
    return {
        "title": topic.title,
        "approx_traffic": topic.approx_traffic,
        "link": topic.link,
        "article": article,
    }


def build_response(geo: str, limit: int) -> dict:
    limit = max(1, min(limit, MAX_LIMIT))
    topics = fetch_trending_topics(geo=geo, limit=limit)

    results = []
    for topic in topics:
        try:
            article = write_article(topic)
        except Exception as exc:  # noqa: BLE001 - 개별 기사 실패는 전체 응답을 막지 않는다.
            article = f"(기사 생성 실패: {exc})"
        results.append(_topic_to_dict(topic, article))

    return {"geo": geo, "count": len(results), "results": results}


class handler(BaseHTTPRequestHandler):  # noqa: N801 - Vercel Python 런타임 규약
    def do_GET(self) -> None:  # noqa: N802
        query = parse_qs(urlparse(self.path).query)
        geo = query.get("geo", ["KR"])[0]
        try:
            limit = int(query.get("limit", [str(MAX_LIMIT)])[0])
        except ValueError:
            limit = MAX_LIMIT

        try:
            payload = build_response(geo, limit)
        except Exception as exc:  # noqa: BLE001
            self._send_json({"error": f"구글 트렌드 조회에 실패했습니다: {exc}"}, status=502)
            return

        self._send_json(payload)

    def _send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
