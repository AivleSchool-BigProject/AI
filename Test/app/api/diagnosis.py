from fastapi import APIRouter, HTTPException, Depends
import os
import json
import pathlib

from app.schema.request import DiagnosisRequest
from app.schema.response import DiagnosisResponse, UserDiagnosisResponse
from app.service.diagnosis_service import DiagnosisService

router = APIRouter()

def get_diagnosis_service():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY가 설정되지 않았습니다.")
    return DiagnosisService(api_key=api_key)

@router.post("/step1", response_model=DiagnosisResponse)
async def analyze_step1(
    request: DiagnosisRequest,
    diagnosis_service: DiagnosisService = Depends(get_diagnosis_service)
):
    """
    Step 1 진단 분석 엔드포인트
    
    **데이터 흐름:**
    1. user_result → Spring에서 DB에 저장 (사용자에게 보여줄 진단 결과)
    2. rag_context → Step 2로 전달 (DB 저장 X, 다음 단계 입력용)
    
    **최종 리포트:**
    - Step 8 완료 후, 모든 RAG 누적 데이터로 최종 리포트 생성
    - 최종 리포트만 DB에 저장
    """
    try:
        # AI 분석 수행
        analysis = diagnosis_service.analyze_diagnosis(request)
        
        # RAG 컨텍스트 생성 (Step 2로 전달할 임시 데이터)
        rag_context = diagnosis_service.create_rag_context(request, analysis)
        
        # 사용자용 결과 (DB 저장용)
        user_result = UserDiagnosisResponse(
            summary=analysis.summary,
            analysis=analysis.analysis,
            key_insights=analysis.key_insights
        )
        
        return DiagnosisResponse(
            user_result=user_result,
            rag_context=rag_context
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 중 오류 발생: {str(e)}")

@router.post("/step1/test")
async def test_diagnosis(diagnosis_service: DiagnosisService = Depends(get_diagnosis_service)):
    """테스트용 엔드포인트 (sample_answers.json 사용)"""
    try:
        # 현재 파일의 디렉토리 기준으로 상위 디렉토리의 sample_answers.json 찾기
        current_dir = pathlib.Path(__file__).parent.parent.parent
        sample_file = current_dir / "sample_answers.json"
        
        with open(sample_file, "r", encoding="utf-8") as f:
            sample = json.load(f)
        
        request = DiagnosisRequest(**sample)
        return await analyze_step1(request, diagnosis_service)
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"sample_answers.json 파일을 찾을 수 없습니다. 경로: {sample_file}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"테스트 중 오류 발생: {str(e)}")
