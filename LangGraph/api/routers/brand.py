#brand.py
from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter()

# Interview
@router.post("/brands/interview")
async def interview(payload: Dict[str, Any]):
    print("[INTERVIEW]", payload)
    return {
        "summary": "AI 인터뷰 진단 요약",
        "analysis": "브랜드 방향성이 비교적 명확합니다.",
        "key_insights": "다음 단계는 네이밍입니다."
    }

# Naming
@router.post("/brands/naming")
async def naming(brand_id: int, payload: Dict[str, Any]):
    print("[NAMING]", brand_id, payload)
    return {
        "name1": "Brandify",
        "name2": "Cloudia",
        "name3": "Truston"
    }

# Concept
@router.post("/brands/concept")
async def concept(brand_id: int, payload: Dict[str, Any]):
    return {
        "concept1": "혁신",
        "concept2": "신뢰",
        "concept3": "확장성"
    }

# Story
@router.post("/brands/story")
async def story(brand_id: int, payload: Dict[str, Any]):
    return {
        "story1": "우리는 작은 아이디어에서 시작했습니다.",
        "story2": "기술로 신뢰를 만듭니다.",
        "story3": "확장 가능한 브랜드의 시작."
    }

# Logo
@router.post("/brands/logo")
async def logo(brand_id: int, payload: Dict[str, Any]):
    return {
        "logo1": "https://placehold.co/512x512?text=LOGO+1",
        "logo2": "https://placehold.co/512x512?text=LOGO+2",
        "logo3": "https://placehold.co/512x512?text=LOGO+3"
    }