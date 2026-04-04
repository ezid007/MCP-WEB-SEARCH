#!/bin/bash
# MCP 웹 검색 서버 실행 스크립트

# 가상 환경 활성화 (존재하는 경우)
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# 의존성 설치
pip install -r requirements.txt

# 서버 실행
python main.py
