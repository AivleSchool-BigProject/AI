from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# 라우터 임포트
from app.api import diagnosis

# 환경변수 로드
load_dotenv()

app = FastAPI(
    title="Brand Consulting AI API",
    description="AI 기반 브랜드 컨설팅 자동화 서비스",
    version="1.0.0"
)

# CORS 설정 (Spring 백엔드와 통신을 위해)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(diagnosis.router, prefix="/api/v1/diagnosis", tags=["Diagnosis"])

@app.get("/")
async def root():
    return {
        "message": "Brand Consulting AI API", 
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
