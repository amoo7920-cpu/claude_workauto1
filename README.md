# 구글 트렌드 상세 기사 작성 에이전트

구글 트렌드(Google Trends)의 실시간 인기 검색어를 조사하고, 각 검색어에 딸린 연관 뉴스
(제목/요약/출처)를 근거로 Claude가 상세 기사를 자동으로 작성해 주는 파이썬 도구입니다.

## 동작 방식

1. 구글이 공개하는 `Trending Now` RSS 피드(`https://trends.google.com/trending/rss?geo=<국가코드>`)를
   내려받아 인기 검색어 목록과 각 검색어의 추정 검색량, 연관 뉴스 정보를 파싱합니다.
2. 검색어별로 수집된 정보를 프롬프트로 구성해 Anthropic Claude API를 호출, 800~1200자 분량의
   상세 기사(마크다운)를 생성합니다.
3. 생성된 기사를 `output/` 폴더에 `01_검색어.md`, `02_검색어.md` … 형식으로 저장합니다.

## 설치

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 설정

`.env.example`을 참고해 `ANTHROPIC_API_KEY`를 환경변수로 설정합니다.

```bash
cp .env.example .env
# .env 파일을 열어 ANTHROPIC_API_KEY 값을 채워 넣으세요.
export $(grep -v '^#' .env | xargs)   # 또는 원하는 방식으로 환경변수 로드
```

## 사용법

```bash
# 1) 트렌드 목록만 확인 (API 비용 없이 빠르게 확인)
python -m google_trends_agent.cli --dry-run --geo KR --limit 10

# 2) 상위 5개 트렌드에 대해 상세 기사 생성
python -m google_trends_agent.cli --geo KR --limit 5 --output-dir output
```

주요 옵션:

| 옵션 | 설명 | 기본값 |
| --- | --- | --- |
| `--geo` | 국가 코드 (KR, US, JP 등) | `KR` |
| `--limit` | 가져올 트렌드 개수 | `5` |
| `--output-dir` | 기사 저장 폴더 | `output` |
| `--model` | 사용할 Claude 모델 | `claude-sonnet-5` (환경변수 `ANTHROPIC_MODEL`로 변경 가능) |
| `--dry-run` | 기사 생성 없이 트렌드 목록만 출력 | - |

## 테스트

네트워크 호출 없이 RSS 파싱 로직과 프롬프트 구성 로직을 검증하는 단위 테스트가 포함되어 있습니다.

```bash
pip install pytest
pytest
```

## 참고 / 제약 사항

- 구글 트렌드 RSS는 비공식적으로 널리 쓰이는 공개 피드이며, 구글 측 정책 변경으로 응답 형식이나
  가용성이 바뀔 수 있습니다.
- 이 저장소를 실행하는 네트워크 환경에 따라 `trends.google.com` 접근이 차단되어 있을 수 있습니다
  (사내 방화벽, 샌드박스 등). 이 경우 다른 네트워크에서 실행하거나 사내 프록시 허용 목록에
  `trends.google.com`을 추가해야 합니다.
- 기사는 RSS에 포함된 연관 뉴스 요약만을 근거로 작성되며, Claude는 그 범위를 벗어나는 사실을
  단정적으로 서술하지 않도록 프롬프트로 제약되어 있습니다. 실제 보도로 활용하려면 원문 뉴스 링크를
  통해 사실 관계를 반드시 재확인하세요.
