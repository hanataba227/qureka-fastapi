import os
from dotenv import load_dotenv
from typing import List

# 환경 변수 로드
load_dotenv()

# API 키 (기본값은 비어있음, 실제 값은 .env에서 로드)
API_KEY = os.getenv("OPENAI_API_KEY", "")

# 기본 설정
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# ngrok 설정
USE_NGROK = os.getenv("USE_NGROK", "false").lower() == "true"
NGROK_BACKEND_URL = os.getenv("NGROK_BACKEND_URL", "")
NGROK_FRONTEND_URL = os.getenv("NGROK_FRONTEND_URL", "")

# 계산된 설정
BASE_URL = os.getenv("BASE_URL", "https://qureka-fastapi.onrender.com")

# CORS 설정
ALLOWED_ORIGINS: List[str] = [
    "http://localhost:5174",  # 프론트엔드 로컬 서버
    "http://localhost:3000",  # Node.JS 로컬 서버
    NGROK_FRONTEND_URL,       # 프론트엔드 ngrok URL
]

# 특별한 설정이 필요한 경우 전체 출처 허용
ALLOW_ALL_ORIGINS = True  # 개발 환경에서만 True로 설정

# 모델 설정
MAX_USER_MESSAGE_TOKENS = 8000
MODEL_NAME = "gpt-4o-mini"
