"""
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
"""

"""
Brand Consulting API Router
FE 요청을 받아 각 단계별 로직을 호출하고 응답을 반환
현재는 구조 검증을 위해 DUMMY DATA를 반환합니다.
"""

from fastapi import APIRouter, HTTPException, Path, Body
from api.schemas.request import (
    DiagnosisRequest, NamingRequest, ConceptRequest, StoryRequest, LogoRequest
)
from api.schemas.response import (
    DiagnosisResponse,
    NamingResponse, NamingCandidate,
    ConceptResponse, ConceptCandidate,
    StoryResponse, StoryCandidate,
    LogoResponse, LogoCandidate
)
import uuid

router = APIRouter()

# LangGraph 앱 초기화 (서버 시작 시 1회 로드)
# 주의: 실제 운영 환경에서는 lifespan 이벤트 핸들러 등에서 관리하는 것이 좋음
from langgraph_system.graph import create_info_graph
from langgraph_system.state import create_initial_state, BrandConsultingState
import json

print("\n[System] LangGraph Workflow Loading...")
workflow_app = create_info_graph()
print("[System] LangGraph Workflow Loaded Successfully.\n")

# =================================================================
# 1. Diagnosis (Step 1)
# =================================================================
@router.post("/step1/diagnosis", response_model=DiagnosisResponse)
async def create_diagnosis(request: DiagnosisRequest):
    """
    Step 1: 진단 (Diagnosis)
    Q&A 입력을 받아 브랜드 상세 진단을 수행합니다.
    """
    # 1. 초기 State 생성
    # brand_id는 실제로는 DB에서 생성하거나 FE에서 전달받아야 함 (여기선 임시 생성)
    brand_id = f"brand_{uuid.uuid4().hex[:8]}"
    initial_state = create_initial_state(brand_id=brand_id, user_id=request.user_id)
    
    # 2. 입력 데이터 주입
    initial_state["step_1_qa"] = request.qa_answers
    initial_state["current_step"] = 1
    
    # 3. LangGraph 실행 (Diagnosis Node)
    # config: thread_id 등을 설정하여 메모리 체크포인트 활용 가능
    config = {"configurable": {"thread_id": brand_id}}
    
    print(f"\n[API] Step 1 Diagnosis 요청 시작 (Brand ID: {brand_id})")
    
    # invoke 실행
    final_state = workflow_app.invoke(initial_state, config=config)
    
    # 4. 결과 추출
    if final_state.get("error_occurred"):
        raise HTTPException(status_code=500, detail=final_state.get("error_message"))
        
    diagnosis_output = final_state.get("diagnosis_result", {})
    analysis = diagnosis_output.get("analysis", {})
    
    print(f"[API] Step 1 완료. Analysis Summary: {analysis.get('summary')[:30]}...")
    
    return DiagnosisResponse(
        brand_id=brand_id,
        step=1,
        analysis=analysis
    )

# =================================================================
# 2. Naming (Step 2)
# =================================================================
@router.post("/step2/naming", response_model=NamingResponse)
async def create_naming(request: NamingRequest):
    """
    Step 2: 네이밍 (Naming)
    Diagnosis 결과와 함께 호출하여 3개의 브랜드명 후보를 생성합니다.
    """
    # 1. State 복원/재구성
    # Stateless API 특성상 이전 단계 Context를 Request로 받아 State를 재구성함
    # (실제 운영 시에는 thread_id 기반으로 Checkpoint에서 로드하는 것이 이상적임)
    
    brand_id = "temp_brand_id" # Request에 brand_id가 없으므로 임시 값 사용하거나 DB 연동 필요
    
    # State 재구성
    state_update = create_initial_state(brand_id=brand_id, user_id=request.user_id)
    state_update["current_step"] = 2
    state_update["diagnosis_context"] = request.diagnosis_context # 핵심 Context 주입
    state_update["step_2_qa"] = request.qa_answers 
    
    # [Fix] Naming Node 등에서 Step 1 데이터를 참조할 수 있으므로 빈 값이라도 주입
    state_update["step_1_qa"] = {} 
    
    # 2. LangGraph 실행 (Naming Node)
    # config에 thread_id를 주더라도, Request로 받은 Context를 우선시하여 State에 주입
    config = {"configurable": {"thread_id": brand_id}} 
    
    print(f"\n[API] Step 2 Naming 요청 시작")
    
    # invoke 실행
    final_state = workflow_app.invoke(state_update, config=config)
    
    # 3. 결과 추출
    if final_state.get("error_occurred"):
        raise HTTPException(status_code=500, detail=final_state.get("error_message"))
        
    candidates_data = final_state.get("naming_candidates", [])
    
    # Flattening: Dict에서 필드 직접 바인딩
    candidates = []
    for cand in candidates_data:
        output = cand.get("output", {})
        candidates.append(NamingCandidate(
            id=cand["candidate_id"], 
            brand_name=output.get("brand_name", ""),
            name_rationale=output.get("name_rationale", "")
        ))
        
    print(f"[API] Step 2 완료. 생성된 후보 수: {len(candidates)}")
    
    return NamingResponse(
        brand_id=brand_id,
        step=2,
        candidates=candidates
    )

# =================================================================
# 3. Concept (Step 3)
# =================================================================

@router.post("/step3/concept", response_model=ConceptResponse)
async def create_concept(request: ConceptRequest):
    """
    Step 3: 컨셉 (Concept)
    Naming 확정 Context와 함께 호출하여 3개의 컨셉 후보를 생성합니다.
    """
    brand_id = "temp_brand_id"
    
    # State 재구성
    state_update = create_initial_state(brand_id=brand_id, user_id=request.user_id)
    state_update["current_step"] = 3
    state_update["diagnosis_context"] = request.diagnosis_context
    state_update["naming_context"] = request.naming_context
    state_update["step_3_qa"] = request.qa_answers
    
    # Validation 우회용 Dummy Data
    state_update["step_1_qa"] = {}
    state_update["step_2_qa"] = {}
    
    print(f"\n[API] Step 3 Concept 요청 시작")
    
    config = {"configurable": {"thread_id": brand_id}}
    final_state = workflow_app.invoke(state_update, config=config)
    
    if final_state.get("error_occurred"):
        raise HTTPException(status_code=500, detail=final_state.get("error_message"))
        
    candidates_data = final_state.get("concept_candidates", [])
    
    # Flattening
    candidates = []
    for cand in candidates_data:
        output = cand.get("output", {})
        candidates.append(ConceptCandidate(
            id=cand["candidate_id"],
            concept_statement=output.get("concept_statement", ""),
            concept_rationale=output.get("concept_rationale", "")
        ))
        
    print(f"[API] Step 3 완료. 생성된 후보 수: {len(candidates)}")
    
    return ConceptResponse(brand_id=brand_id, step=3, candidates=candidates)

# =================================================================
# 4. Story (Step 4)
# =================================================================
@router.post("/step4/story", response_model=StoryResponse)
async def create_story(request: StoryRequest):
    """
    Step 4: 스토리 (Story)
    Step 1~3 Context와 함께 호출하여 3개의 스토리 후보를 생성합니다.
    """
    brand_id = "temp_brand_id"
    
    # State 재구성
    state_update = create_initial_state(brand_id=brand_id, user_id=request.user_id)
    state_update["current_step"] = 4
    state_update["diagnosis_context"] = request.diagnosis_context
    state_update["naming_context"] = request.naming_context
    state_update["concept_context"] = request.concept_context
    state_update["step_4_qa"] = request.qa_answers
    
    # Validation 우회용 Dummy Data
    state_update["step_1_qa"] = {}
    state_update["step_2_qa"] = {}
    state_update["step_3_qa"] = {}
    
    print(f"\n[API] Step 4 Story 요청 시작")
    
    config = {"configurable": {"thread_id": brand_id}}
    final_state = workflow_app.invoke(state_update, config=config)
    
    if final_state.get("error_occurred"):
        raise HTTPException(status_code=500, detail=final_state.get("error_message"))
        
    candidates_data = final_state.get("story_candidates", [])
    
    # Flattening
    candidates = []
    for cand in candidates_data:
        output = cand.get("output", {})
        candidates.append(StoryCandidate(
            id=cand["candidate_id"],
            brand_story=output.get("brand_story", ""),
            story_rationale=output.get("story_rationale", "")
        ))
        
    print(f"[API] Step 4 완료. 생성된 후보 수: {len(candidates)}")
    
    return StoryResponse(brand_id=brand_id, step=4, candidates=candidates)

# =================================================================
# 5. Logo (Step 5)
# =================================================================
@router.post("/step5/logo", response_model=LogoResponse)
async def create_logo(request: LogoRequest):
    """
    Step 5: 로고 (Logo)
    모든 데이터 Context와 함께 호출하여 3개의 로고 이미지 후보를 생성합니다.
    """
    brand_id = "temp_brand_id"
    
    # State 재구성
    state_update = create_initial_state(brand_id=brand_id, user_id=request.user_id)
    state_update["current_step"] = 5
    state_update["diagnosis_context"] = request.diagnosis_context
    state_update["naming_context"] = request.naming_context
    state_update["concept_context"] = request.concept_context
    state_update["story_context"] = request.story_context
    state_update["step_5_qa"] = request.qa_answers
    
    # Validation 우회용 Dummy Data
    state_update["step_1_qa"] = {}
    state_update["step_2_qa"] = {}
    state_update["step_3_qa"] = {}
    state_update["step_4_qa"] = {}
    
    print(f"\n[API] Step 5 Logo 요청 시작")
    
    config = {"configurable": {"thread_id": brand_id}}
    final_state = workflow_app.invoke(state_update, config=config)
    
    if final_state.get("error_occurred"):
        raise HTTPException(status_code=500, detail=final_state.get("error_message"))
        
    candidates_data = final_state.get("logo_candidates", [])
    
    # Flattening
    candidates = []
    for cand in candidates_data:
        output = cand.get("output", {})
        candidates.append(LogoCandidate(
            id=cand["candidate_id"],
            logo_image_url=output.get("logo_image_url", ""),
            logo_concept=output.get("logo_concept", "")
        ))
        
    print(f"[API] Step 5 완료. 생성된 후보 수: {len(candidates)}")
    
    return LogoResponse(brand_id=brand_id, step=5, candidates=candidates)

# =================================================================
# [Regeneration]
# =================================================================
# [Regeneration Logic Removed]
