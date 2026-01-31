"""
FastAPI Response DTOs
AI -> BE -> FE 흐름에서 반환되는 응답 데이터 구조 정의
항상 3개의 후보군(Candidates)을 포함 (Step 1 제외)
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

# =================================================================
# [Common] 공통 응답 구조
# =================================================================
class BaseResponse(BaseModel):
    brand_id: str = Field(..., description="브랜드 ID")
    step: int = Field(..., description="현재 단계 번호")

class CandidateItem(BaseModel):
    """
    개별 후보 아이템
    Value(결과물) + Rationale(설명) 쌍
    """
    id: int = Field(..., description="후보 ID (0, 1, 2)")
    output: Dict[str, Any] = Field(..., description="AI 생성 결과물 (Value + Rationale)")

class GenerationResponse(BaseResponse):
    """
    생성 결과 응답 (Step 2~5)
    3개의 후보 리스트 포함
    """
    candidates: List[CandidateItem] = Field(..., description="3개의 생성 후보 리스트")

# =================================================================
# [Step 1] 진단 (Diagnosis) Response
# =================================================================
class DiagnosisResponse(BaseResponse):
    """
    Step 1: 진단 결과 방출 (후보 선택 없음)
    """
    analysis: Dict[str, Any] = Field(..., description="진단 분석 결과 (Summary, Keywords, Persona, Perspectives)")

# =================================================================
# [Step 2] 네이밍 (Naming) Output Field
# =================================================================
# Candidate Output 구조 예시 문서화용 (실제 응답은 Dict[str, Any]로 유연하게 처리)
class NamingOutput(BaseModel):
    brand_name: str
    name_rationale: str

# =================================================================
# [Step 3] 컨셉 (Concept) Output Field
# =================================================================
class ConceptOutput(BaseModel):
    concept_statement: str
    concept_rationale: str

# =================================================================
# [Step 4] 스토리 (Story) Output Field
# =================================================================
class StoryOutput(BaseModel):
    brand_story: str
    story_rationale: str

# =================================================================
# [Step 5] 로고 (Logo) Output Field
# =================================================================
class LogoOutput(BaseModel):
    logo_image_url: str
    logo_concept: str # Rationale 대신 Concept 설명 포함
