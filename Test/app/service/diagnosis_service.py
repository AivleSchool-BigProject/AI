import json
from openai import OpenAI
from typing import Dict, Any
from app.schema.request import DiagnosisRequest
from app.schema.response import DiagnosisAnalysis, RAGContext, RawAnswers

class DiagnosisService:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
    
    def analyze_diagnosis(self, request: DiagnosisRequest) -> DiagnosisAnalysis:
        """질문-답변을 분석하여 요약/분석 리포트 생성"""
        
        # Q&A 텍스트 생성
        qa_text = f"""
Q: 우리 서비스를 전혀 모르는 10살 조카에게 설명한다고 가정하고, 한 문장으로 서비스를 정의해주세요.
A: {request.s1_one_line_definition}

Q: 고객이 우리 서비스를 쓰지 않을 때 겪는 가장 고통스러운 문제점은 무엇인가요?
A: {request.s1_core_problem}

Q: 우리 서비스의 '찐팬'이 될 핵심 고객층은 누구인가요?
A: {request.s1_target_persona.value}

Q: 경쟁사가 절대 따라 할 수 없는 우리만의 '무기'는 무엇인가요?
A: {request.s1_differentiation}

Q: 현재 비즈니스의 완성도는 어느 정도인가요?
A: {request.s1_growth_stage.value}

Q: 비즈니스가 속한 산업군은 어디인가요?
A: {request.s1_industry.value}

Q: 5년 뒤, 우리 회사가 뉴스 헤드라인에 나온다면 어떤 제목일까요?
A: {request.s1_vision}
"""
        
        system_prompt = """당신은 브랜드 컨설팅 전문가입니다.
고객의 진단 답변을 분석하여 간결한 요약과 분석을 JSON으로 제공하세요.

출력 형식:
{
  "summary": "비즈니스를 한 문장으로 요약",
  "keywords": ["키워드1", "키워드2", "키워드3", "키워드4", "키워드5"],
  "analysis": "타겟, 시장, 브랜드 방향성을 통합한 핵심 분석 (300자 이내)",
  "key_insights": "핵심 인사이트 및 제안사항 (3-4문장)"
}"""
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"다음 진단 답변을 분석해주세요:\n\n{qa_text}"}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        analysis_dict = json.loads(response.choices[0].message.content)
        return DiagnosisAnalysis(**analysis_dict)
    
    def create_rag_context(self, request: DiagnosisRequest, analysis: DiagnosisAnalysis) -> RAGContext:
        """RAG용 컨텍스트 생성"""
        raw_answers = RawAnswers(
            service_definition=request.s1_one_line_definition,
            pain_point=request.s1_core_problem,
            target_persona=request.s1_target_persona.value,
            usp=request.s1_differentiation,
            growth_stage=request.s1_growth_stage.value,
            industry=request.s1_industry.value,
            vision=request.s1_vision
        )
        
        return RAGContext(
            step_1_analysis=analysis,
            step_1_raw_answers=raw_answers
        )
