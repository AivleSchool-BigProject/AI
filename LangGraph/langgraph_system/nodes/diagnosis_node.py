"""
Step 1: Diagnosis Node
초기 진단 단계 - 비즈니스 핵심 파악
"""
from langgraph_system.state import BrandConsultingState, get_cumulative_key
from langgraph_system.utils import get_openai_client, validate_step_input
from langgraph_system.prompts import GenerationPrompts
from database.connection import db_connection
from database.operations import save_brand_result, update_brand_step
import json


def diagnosis_node(state: BrandConsultingState) -> BrandConsultingState:
    """
    Step 1: 초기 진단 노드 (Diagnosis)
    
    [Input]
    - step_1_qa: 사용자 응답 데이터
    
    [Process]
    - Business, User, Market 3가지 관점 분석
    - 종합 진단 요약, 핵심 키워드, 타겟 페르소나 추출
    
    [Output]
    - diagnosis_result: 전체 분석 결과 (JSON)
    - diagnosis_context: 다음 단계 전달용 핵심 데이터 Subset
    """
    print(f"\n{'='*60}")
    print(f"[Step 1: Diagnosis] 실행 시작 (Brand ID: {state.get('brand_id')})")
    print(f"{'='*60}")
    
    # 1. 입력 검증
    step_1_qa = state.get("step_1_qa")
    if not validate_step_input(1, {"answers": step_1_qa} if step_1_qa else None):
        state["error_occurred"] = True
        state["error_message"] = "Step 1 Q&A 데이터가 없습니다."
        return state
    
    # 2. OpenAI 클라이언트 생성
    try:
        client = get_openai_client()
    except Exception as e:
        state["error_occurred"] = True
        state["error_message"] = f"OpenAI 클라이언트 생성 실패: {e}"
        return state
    
    # 3. 프롬프트 준비 (prompts.py 활용)
    system_prompt = GenerationPrompts.DIAGNOSIS_SYSTEM
    user_prompt = GenerationPrompts.DIAGNOSIS_USER.format(
        qa_data=json.dumps(step_1_qa, ensure_ascii=False, indent=2)
    )
    
    # 4. GPT-4 호출
    try:
        print("[Step 1] GPT-4 비즈니스 진단 분석 중...")
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        analysis_data = json.loads(resp.choices[0].message.content)
        print("[Step 1] 분석 완료: 3가지 관점 및 핵심 요소 추출됨")
        
    except Exception as e:
        print(f"[Step 1] ❌ GPT-4 분석 실패: {e}")
        # 실패 시 기본값 (Fallback)
        analysis_data = {
            "summary": "분석 실패 (기본값)",
            "keywords": ["Error"],
            "persona": "Unknown",
            "perspectives": {}
        }
    
    # 5. 결과 구성
    # 5-1. Diagnosis Result (전체 저장용)
    # 사용자 요구 포맷: { "summary": "...", "keywords": [], "persona": "...", "perspectives": {...} }
    diagnosis_output = {
        "summary": analysis_data.get("summary", ""),
        "keywords": analysis_data.get("keywords", []),
        "persona": analysis_data.get("persona", ""),
        "perspectives": analysis_data.get("perspectives", {})
    }
    
    diagnosis_result = {
        "qa": step_1_qa,
        "analysis": diagnosis_output  # 이 자체가 output이자 analysis 역할
    }
    state["diagnosis_result"] = diagnosis_result
    
    # 5-2. Diagnosis Context (다음 단계 전달용)
    # Step 2 Naming 등에서 사용할 핵심 정보만 추출
    diagnosis_context = {
        "diagnosis_summary": diagnosis_output["summary"],
        "core_keywords": diagnosis_output["keywords"],
        "target_persona": diagnosis_output["persona"],
        # 필요 시 perspectives도 추가 가능하나, 일단 핵심 3요소 위주로 전달
        "perspectives": diagnosis_output["perspectives"]
    }
    state["diagnosis_context"] = diagnosis_context
    state["step_1_analysis"] = diagnosis_output # 기존 호환성 유지 (선택사항)
    
    print(f"[Step 1] Context 설정 완료: {list(diagnosis_context.keys())}")

    # 6. DB 저장 (옵션)
    try:
        session = db_connection.get_session()
        save_brand_result(
            session=session,
            brand_id=state["brand_id"],
            step_name="diagnosis",
            result_data=diagnosis_result
        )
        update_brand_step(session, state["brand_id"], 2)
        session.close()
        print("[Step 1] ✅ DB 저장 완료")
    except Exception as e:
        print(f"[Step 1] ⚠️ DB 저장 실패 (Skip): {e}")
    
    # 7. 상태 업데이트
    state["current_step"] = 2
    
    print(f"[Step 1] ✅ 완료")
    print(f"  - 키워드: {diagnosis_output['keywords']}")
    print(f"  - 페르소나: {diagnosis_output['persona']}")
    print(f"{'='*60}\n")
    
    return state
