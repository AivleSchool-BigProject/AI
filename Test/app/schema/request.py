from pydantic import BaseModel

class TargetPersona(BaseModel):
    id: str
    text: str
    value: str

class GrowthStage(BaseModel):
    id: str
    text: str
    value: str

class Industry(BaseModel):
    id: str
    text: str
    value: str

class DiagnosisRequest(BaseModel):
    """Step 1 진단 요청 모델"""
    s1_one_line_definition: str
    s1_core_problem: str
    s1_target_persona: TargetPersona
    s1_differentiation: str
    s1_growth_stage: GrowthStage
    s1_industry: Industry
    s1_vision: str
