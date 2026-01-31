"""
FastAPI Request DTOs
FE -> BE -> AI 흐름에서 사용되는 요청 데이터 구조 정의
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

# =================================================================
# [Base Request] - 공통 요청 헤더/메타데이터
# =================================================================
class BaseRequest(BaseModel):
    user_id: str = Field(..., description="사용자 ID")

# =================================================================
# [Step 1] 진단 (Diagnosis) Request
# =================================================================
class DiagnosisRequest(BaseRequest):
    """
    Step 1: 진단 요청
    FE 입력: Q&A 답변
    """
    qa_answers: Dict[str, Any] = Field(..., description="Step 1 Q&A 답변 (JSON)")

# =================================================================
# [Step 2] 네이밍 (Naming) Request
# =================================================================
class NamingRequest(BaseRequest):
    """
    Step 2: 네이밍 생성 요청
    FE 입력: Step 1 결과(Context) + Step 2 Q&A
    """
    diagnosis_context: Dict[str, Any] = Field(..., description="Step 1 진단 결과 (핵심 키워드, 페르소나 등)")
    qa_answers: Dict[str, Any] = Field(..., description="Step 2 Q&A 답변")

# =================================================================
# [Step 3] 컨셉 (Concept) Request
# =================================================================
class ConceptRequest(BaseRequest):
    """
    Step 3: 컨셉 생성 요청
    FE 입력: Step 1, 2 Context + Step 3 Q&A
    """
    diagnosis_context: Dict[str, Any] = Field(..., description="Step 1 진단 결과")
    naming_context: Dict[str, Any] = Field(..., description="Step 2 네이밍 선택 결과 (브랜드명, 선정 이유)")
    qa_answers: Dict[str, Any] = Field(..., description="Step 3 Q&A 답변")

# =================================================================
# [Step 4] 스토리 (Story) Request
# =================================================================
class StoryRequest(BaseRequest):
    """
    Step 4: 스토리 생성 요청
    FE 입력: Step 1~3 Context + Step 4 Q&A
    """
    diagnosis_context: Dict[str, Any] = Field(..., description="Step 1 진단 결과")
    naming_context: Dict[str, Any] = Field(..., description="Step 2 네이밍 선택 결과")
    concept_context: Dict[str, Any] = Field(..., description="Step 3 컨셉 선택 결과")
    qa_answers: Dict[str, Any] = Field(..., description="Step 4 Q&A 답변")

# =================================================================
# [Step 5] 로고 (Logo) Request
# =================================================================
class LogoRequest(BaseRequest):
    """
    Step 5: 로고 생성 요청
    FE 입력: Step 1~4 Context + Step 5 Q&A
    """
    diagnosis_context: Dict[str, Any] = Field(..., description="Step 1 진단 결과")
    naming_context: Dict[str, Any] = Field(..., description="Step 2 네이밍 선택 결과")
    concept_context: Dict[str, Any] = Field(..., description="Step 3 컨셉 선택 결과")
    story_context: Dict[str, Any] = Field(..., description="Step 4 스토리 선택 결과")
    qa_answers: Dict[str, Any] = Field(..., description="Step 5 Q&A 답변")

# =================================================================
# [재생성] Regenerate Request
# =================================================================
class RegenerateRequest(BaseRequest):
    """
    재생성 요청
    사용자가 생성된 후보에 만족하지 못할 때 피드백과 함께 요청
    """
    original_request: Dict[str, Any] = Field(..., description="원래 요청했던 Request Body (Context 포함)")
    feedback: str = Field(..., description="재생성 요청 피드백 (한국어)")
    step: int = Field(..., description="재생성 할 단계 번호 (2~5)")
