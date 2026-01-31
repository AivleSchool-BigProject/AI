from pydantic import BaseModel
from typing import List

class DiagnosisAnalysis(BaseModel):
    """분석 결과"""
    summary: str
    keywords: List[str]
    analysis: str
    key_insights: str

class UserDiagnosisResponse(BaseModel):
    """사용자용 응답 (DB 저장용)"""
    summary: str
    analysis: str
    key_insights: str

class RawAnswers(BaseModel):
    """원본 답변"""
    service_definition: str
    pain_point: str
    target_persona: str
    usp: str
    growth_stage: str
    industry: str
    vision: str

class RAGContext(BaseModel):
    """RAG용 컨텍스트"""
    step_1_analysis: DiagnosisAnalysis
    step_1_raw_answers: RawAnswers

class DiagnosisResponse(BaseModel):
    """전체 응답"""
    user_result: UserDiagnosisResponse
    rag_context: RAGContext
