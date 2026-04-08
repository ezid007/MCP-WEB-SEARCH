# RooCode MCP 웹 검색 서버

RooCode 커스텀 에이전트에 웹 검색 기능을 추가하는 MCP 서버입니다.
**DuckDuckGo 를 기본 검색 엔진으로 사용하며, Rate limit 발생 시 Google Custom Search API 로 자동 폴백합니다.**

## 프로젝트 구조

```
mcp-web-search/
├── main.py                 # MCP 서버 메인 파일
├── requirements.txt        # Python 의존성
├── .env                    # 환경 변수 (API 키)
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

### 2. 환경 변수 설정 (Google Custom Search API 사용 시)

Google Custom Search API 를 사용하려면 `.env` 파일을 생성하고 API 키를 설정하세요:

```bash
# .env 파일 생성
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CSE_ID=your_google_cse_id_here
```

**.env 파일은 `.gitignore` 에 포함되어 GitHub 에 공유되지 않습니다.**

#### Google API 키 발급 방법

1. **Google Cloud Console** 로 이동
   - https://console.cloud.google.com/apis/credentials

2. **새 프로젝트 생성** (선택)
   - 상단 프로젝트 드롭다운 → "새 프로젝트"
   - 프로젝트 이름 입력 → "생성"

3. **Custom Search API 활성화**
   - https://console.cloud.google.com/apis/library/customsearch.googleapis.com
   - "사용" 버튼 클릭

4. **API 키 생성**
   - https://console.cloud.google.com/apis/credentials
   - "크레덴셜 생성" → "API 키"
   - 생성된 API 키 복사

5. **Custom Search Engine (CSE) 생성**
   - https://programmablesearchengine.google.com/controlpanel/create
   - "검색할 웹페이지": "전체 웹" 선택
   - "검색 엔진 이름": 원하는 이름 입력
   - 생성 후 "검색 엔진 모두"에서 CSE ID 확인 (16 자리 문자열)

6. **.env 파일에 설정**
   ```
   GOOGLE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXX
   GOOGLE_CSE_ID=0123456789abcdef
   ```

**참고:** Google Custom Search API 는 하루 100 회 무료 쿼트 제공, 초과 시 $5/1000 회 청구

### 3. 서버 테스트

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
            "args": ["/path/to/mcp-web-search/main.py"],
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

## 작동 원리

1. **기본 검색**: DuckDuckGo 를 사용하여 검색
2. **Rate limit 감지**: DuckDuckGo 가 Rate limit(202) 을 반환하면
3. **자동 폴백**: Google Custom Search API 로 자동 전환
4. **결과 반환**: 사용 가능한 검색 엔진에서 결과를 반환

## 문제 해결

### 서버가 시작되지 않음

1. Python 버전을 확인하세요 (3.8+ 권장):

```bash
python --version
```

2. 의존성이 제대로 설치되었는지 확인:

```bash
pip list | grep -E "mcp|duckduckgo|google"
```

### Google API 오류

1. `.env` 파일이 올바른지 확인
2. API 키와 CSE ID 가 설정되었는지 확인
3. Google Cloud Console 에서 Custom Search API 가 활성화되었는지 확인

### 검색 결과가 없음

1. 인터넷 연결 확인
2. 검색 쿼리가 적절한지 확인
3. 지역 코드를 변경해 보세요 (예: "us-en")

### DuckDuckGo Rate limit

DuckDuckGo 는 IP 주소당 요청 횟수를 제한합니다. Rate limit 이 발생하면:
- 잠시 대기 후 다시 시도 (10-30 분)
- Google Custom Search API 로 자동 폴백 (설정된 경우)

## 라이선스

MIT License

# MCP-WEB-SEARCH
