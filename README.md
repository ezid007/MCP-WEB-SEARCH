# RooCode MCP 웹 검색 서버

RooCode 커스텀 에이전트에 DuckDuckGo 웹 검색 기능을 추가하는 MCP 서버입니다.

## 프로젝트 구조

```
mcp-web-search/
├── main.py                 # MCP 서버 메인 파일
├── requirements.txt        # Python 의존성
├── run.sh                 # 실행 스크립트
├── roo-code-settings.example.json  # RooCode 설정 예시
└── README.md              # 이 파일
```

## 설치 방법

### 1. 의존성 설치

```bash
cd mcp-web-search
pip install -r requirements.txt
```

또는 가상 환경을 사용:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 또는
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. 서버 테스트

서버가 정상적으로 작동하는지 테스트:

```bash
python main.py
```

서버가 시작되면 STDIO 를 통해 MCP 프로토콜을 대기합니다.

## RooCode 설정 방법

### 방법 1: RooCode 설정 파일에 추가

1. `~/.roo/settings.json` (또는 작업 공간 설정) 에 다음을 추가:

```json
{
    "mcpServers": {
        "web-search": {
            "command": "python",
            "args": ["/home/aiis/a_test/mcp-web-search/main.py"],
            "disabled": false,
            "timeout": 30
        }
    }
}
```

### 방법 2: 작업 공간 설정

프로젝트 루트에 `.vscode/settings.json` 을 생성:

```json
{
    "roo-code.mcpServers": {
        "web-search": {
            "command": "python",
            "args": ["${workspaceFolder}/mcp-web-search/main.py"],
            "disabled": false,
            "timeout": 30
        }
    }
}
```

## 사용 방법

RooCode 에이전트에게 웹 검색을 요청하세요:

**예시 프롬프트:**

```
"Python 3.12 의 새로운 기능에 대해 검색해서 알려줘."
```

**또는:**

```
"오늘 서울의 날씨 정보를 웹에서 찾아줘."
```

에이전트가 자동으로 `web_search` 도구를 사용하여 검색 결과를 반환합니다.

## 도구 스키마

### web_search

웹 검색을 수행합니다.

**매개변수:**

- `query` (필수): 검색 쿼리
- `max_results` (선택): 최대 결과 수 (기본값: 10, 최대: 50)
- `region` (선택): 지역 코드 (기본값: "kr-ko")

**예시:**

```json
{
    "query": "Python 프로그래밍 튜토리얼",
    "max_results": 5,
    "region": "kr-ko"
}
```

## 커스터마이징

### 다른 검색 엔진 사용

DuckDuckGo 대신 다른 검색 엔진을 사용하려면 `main.py` 의 `perform_web_search` 함수를 수정하세요.

예: Google Custom Search 사용

```python
from googlesearch import search

def perform_web_search(query: str, max_results: int = 10, region: str = "kr-ko") -> list[dict]:
    results = []
    for i, url in enumerate(search(query, num=max_results), 1):
        results.append({
            "rank": i,
            "url": url,
            "title": "제목 없음",
            "snippet": "설명 없음"
        })
    return results
```

### 추가 도구 구현

`WEB_SEARCH_TOOL` 을 복사하여 새로운 도구를 추가할 수 있습니다:

```python
NEWS_SEARCH_TOOL = Tool(
    name="news_search",
    description="뉴스 검색을 수행합니다.",
    inputSchema={...}
)

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [WEB_SEARCH_TOOL, NEWS_SEARCH_TOOL]
```

## 문제 해결

### 서버가 시작되지 않음

1. Python 버전을 확인하세요 (3.8+ 권장):

```bash
python --version
```

2. 의존성이 제대로 설치되었는지 확인:

```bash
pip list | grep -E "mcp|duckduckgo"
```

### RooCode 가 도구를 찾지 못함

1. 설정 파일 경로가 올바른지 확인
2. RooCode 를 재시작
3. 설정 파일의 JSON 문법 오류 확인

### 검색 결과가 없음

1. 인터넷 연결 확인
2. 검색 쿼리가 적절한지 확인
3. 지역 코드를 변경해 보세요 (예: "us-en")

## 라이선스

MIT License

# MCP-WEB-SEARCH
