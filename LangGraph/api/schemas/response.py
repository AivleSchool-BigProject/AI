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

# =================================================================
# [Step 1] 진단 (Diagnosis) Response
# =================================================================
class DiagnosisResponse(BaseResponse):
    """
    Step 1: 진단 결과 (후보 선택 없음)
    """
    analysis: Dict[str, Any] = Field(..., description="진단 분석 결과 (Summary, Keywords, Persona, Perspectives)")

# =================================================================
# [Step 2] 네이밍 (Naming) Response
# =================================================================
class NamingCandidate(BaseModel):
    id: int = Field(..., description="후보 ID (0, 1, 2)")
    brand_name: str = Field(..., description="제안된 브랜드명")
    name_rationale: str = Field(..., description="네이밍 선정 이유")

class NamingResponse(BaseResponse):
    candidates: List[NamingCandidate] = Field(..., description="네이밍 후보 리스트")

# =================================================================
# [Step 3] 컨셉 (Concept) Response
# =================================================================
class ConceptCandidate(BaseModel):
    id: int = Field(..., description="후보 ID (0, 1, 2)")
    concept_statement: str = Field(..., description="컨셉 슬로건/문구")
    concept_rationale: str = Field(..., description="컨셉 기획 의도")

class ConceptResponse(BaseResponse):
    candidates: List[ConceptCandidate] = Field(..., description="컨셉 후보 리스트")

# =================================================================
# [Step 4] 스토리 (Story) Response
# =================================================================
class StoryCandidate(BaseModel):
    id: int = Field(..., description="후보 ID (0, 1, 2)")
    brand_story: str = Field(..., description="브랜드 스토리 (Short ver.)")
    story_rationale: str = Field(..., description="스토리 구성 의도")

class StoryResponse(BaseResponse):
    candidates: List[StoryCandidate] = Field(..., description="스토리 후보 리스트")

# =================================================================
# [Step 5] 로고 (Logo) Response
# =================================================================
class LogoCandidate(BaseModel):
    id: int = Field(..., description="후보 ID (0, 1, 2)")
    logo_image_url: str = Field(..., description="생성된 로고 이미지 URL")
    logo_concept: str = Field(..., description="로고 디자인 컨셉 설명")

class LogoResponse(BaseResponse):
    candidates: List[LogoCandidate] = Field(..., description="로고 후보 리스트")
