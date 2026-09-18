"""구글 트렌드 기반 상세 기사 자동 작성 에이전트의 커맨드라인 인터페이스."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Optional, Sequence

from .article_writer import DEFAULT_MODEL, write_article
from .trends_fetcher import fetch_trending_topics


def _slugify(text: str, max_len: int = 40) -> str:
    slug = re.sub(r"[^0-9A-Za-z가-힣]+", "-", text).strip("-")
    return (slug or "trend")[:max_len]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="구글 트렌드 인기 검색어를 수집하고 Claude로 상세 기사를 작성합니다.",
    )
    parser.add_argument("--geo", default="KR", help="국가 코드 (기본값: KR)")
    parser.add_argument("--limit", type=int, default=5, help="가져올 트렌드 개수 (기본값: 5)")
    parser.add_argument(
        "--output-dir", default="output", help="기사를 저장할 폴더 (기본값: output)"
    )
    parser.add_argument(
        "--model", default=DEFAULT_MODEL, help=f"사용할 Claude 모델 (기본값: {DEFAULT_MODEL})"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="기사를 생성하지 않고 수집된 트렌드 목록만 출력합니다.",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        topics = fetch_trending_topics(geo=args.geo, limit=args.limit)
    except Exception as exc:  # noqa: BLE001 - CLI 최상위에서 실패 사유를 알려준다.
        print(f"구글 트렌드 데이터를 가져오지 못했습니다: {exc}", file=sys.stderr)
        return 1

    if not topics:
        print("가져온 트렌드가 없습니다.", file=sys.stderr)
        return 1

    if args.dry_run:
        for i, topic in enumerate(topics, 1):
            traffic = topic.approx_traffic or "알수없음"
            print(f"{i}. {topic.title} (추정 검색량: {traffic}, 관련뉴스 {len(topic.news_items)}건)")
        return 0

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    failures = 0
    for i, topic in enumerate(topics, 1):
        print(f"[{i}/{len(topics)}] '{topic.title}' 기사 작성 중...")
        try:
            article = write_article(topic, model=args.model)
        except Exception as exc:  # noqa: BLE001
            print(f"  실패: {exc}", file=sys.stderr)
            failures += 1
            continue

        filename = out_dir / f"{i:02d}_{_slugify(topic.title)}.md"
        filename.write_text(article, encoding="utf-8")
        print(f"  저장됨: {filename}")

    return 1 if failures == len(topics) else 0


if __name__ == "__main__":
    sys.exit(main())
