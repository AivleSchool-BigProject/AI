"""
FastAPI 설정 파일
환경 변수 및 앱 설정 관리
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """
    애플리케이션 설정
    .env 파일에서 자동으로 로드됨
    """
    # API 서버 설정
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_TITLE: str = "Brand Consulting AI API"
    API_VERSION: str = "1.0.0"
    
    # CORS 설정
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # 세션 설정
    SESSION_TIMEOUT: int = 3600  # 1시간 (초 단위)
    MAX_SESSIONS: int = 100  # 최대 동시 세션 수
    
    # OpenAI (기존 .env에서 로드)
    OPENAI_API_KEY: str = ""
    
    # 데이터베이스 (기존 설정)
    ENABLE_DB: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 전역 설정 인스턴스
settings = Settings()
