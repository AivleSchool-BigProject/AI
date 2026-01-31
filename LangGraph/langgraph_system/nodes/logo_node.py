"""
Step 5: Logo Node
로고 디자인 가이드 생성 + 이미지 자동 생성 + Brand Consulting Report 생성
"""
from langgraph_system.state import BrandConsultingState
from langgraph_system.utils import get_openai_client, validate_step_input
from langgraph_system.prompts import GenerationPrompts
import json
import os
import requests
from datetime import datetime

def logo_node(state: BrandConsultingState) -> BrandConsultingState:
    """
    Step 5: 로고 디자인 가이드 생성 + 이미지 자동 생성 + Report
    
    [Process]
    1. GPT-4: 로고 컨셉 및 DALL-E 프롬프트 3가지 생성
    2. DALL-E 3: 생성된 3가지 프롬프트로 즉시 이미지 생성
    3. Brand Consulting Report: 최종 리포트 생성
    
    [Output]
    - logo_candidates: logo_concept, logo_image_url
    - brand_consulting_report
    """
    print(f"\n{'='*60}")
    print(f"[Step 5: Logo] 실행 시작 (Brand ID: {state.get('brand_id')})")
    print(f"{'='*60}")
    
    # 1. 입력 검증
    step_5_qa = state.get("step_5_qa")
    if not validate_step_input(5, {"answers": step_5_qa} if step_5_qa else None):
        state["error_occurred"] = True
        state["error_message"] = "Step 5 Q&A 데이터가 없습니다."
        return state
    
    # 2. Context 확인
    naming_context = state.get("naming_context")
    concept_context = state.get("concept_context")
    story_context = state.get("story_context")
    diagnosis_context = state.get("diagnosis_context")

    if not all([naming_context, concept_context, story_context, diagnosis_context]):
        print("⚠️ [Step 5] 일부 이전 단계 Context가 누락되었습니다.")

    # 3. OpenAI 클라이언트
    try:
        client = get_openai_client()
    except Exception as e:
        state["error_occurred"] = True
        state["error_message"] = f"Client Error: {e}"
        return state
    
    # 4. 재생성 피드백
    feedback_section = ""
    if state.get("feedback_required") and state.get("feedback_content"):
        print(f"[Step 5] 🔄 재생성 피드백 반영: {state.get('feedback_content')}")
        feedback_section = f"""
        [User Feedback for Regeneration]
        Feedback: "{state.get('feedback_content')}"
        IMPORTANT: Reflect feedback in new logo concepts.
        """

    # 5. 프롬프트 구성 (컨셉 생성용)
    system_prompt = GenerationPrompts.LOGO_SYSTEM
    user_prompt = GenerationPrompts.LOGO_USER.format(
        brand_name=naming_context.get("brand_name", "") if naming_context else "Brand",
        concept_statement=concept_context.get("concept_statement", "") if concept_context else "",
        brand_story=story_context.get("brand_story", "") if story_context else "",
        core_keywords=str(diagnosis_context.get("core_keywords", [])) if diagnosis_context else "",
        qa_data=json.dumps(step_5_qa, ensure_ascii=False, indent=2),
        feedback_section=feedback_section
    )
    
    # 6. GPT-4 로고 컨셉 및 프롬프트 생성
    logo_options = []
    try:
        print("[Step 5] 1단계: GPT-4o 로고 프롬프트 작성 중...")
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        logo_response = json.loads(resp.choices[0].message.content)
        logo_options = logo_response.get("options", [])
        
        if len(logo_options) < 3:
            while len(logo_options) < 3:
                logo_options.append({
                    "logo_concept": f"Logo {len(logo_options)+1}",
                    "dalle_prompt": "Create a modern logo",
                    "color_palette": []
                })
        
    except Exception as e:
        print(f"[Step 5] ❌ 컨셉 생성 실패: {e}")
        state["error_occurred"] = True
        state["error_message"] = str(e)
        return state

    # 7. DALL-E 3 이미지 생성 (순차 처리)
    output_dir = "generated_logos"
    os.makedirs(output_dir, exist_ok=True)
    brand_id = state.get("brand_id", "unknown")
    
    candidates = []
    print(f"\n[Step 5] 2단계: DALL-E 3 이미지 생성 시작 (총 {len(logo_options)}장)")
    
    for idx, opt in enumerate(logo_options):
        dalle_prompt = opt.get("dalle_prompt", "Logo design")
        print(f"  - [Image {idx+1}/{len(logo_options)}] 생성 중... (Prompt: {dalle_prompt[:30]}...)")
        
        image_url = None
        image_path = None
        
        try:
            # DALL-E 3 호출
            img_resp = client.images.generate(
                model="dall-e-3",
                prompt=dalle_prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )
            image_url = img_resp.data[0].url
            
            # 로컬 저장
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{brand_id}_logo_{idx}_{timestamp}.png"
            image_path = os.path.join(output_dir, filename)
            
            img_data = requests.get(image_url).content
            with open(image_path, 'wb') as f:
                f.write(img_data)
                
            print(f"    ✅ 생성 완료: {filename}")
            
        except Exception as e:
            print(f"    ❌ 이미지 생성 실패: {e}")
            # 실패 시에도 진행은 하되 URL은 None
        
        candidates.append({
            "candidate_id": idx,
            "output": {
                "logo_concept": opt.get("logo_concept", "N/A"),
                "logo_image_url": image_url,
                "logo_image_path": image_path  # 파일 저장을 위해 임시 유지
            }
        })
    
    state["logo_candidates"] = candidates
    state["current_step"] = 6 # Human Review로 이동
    
    print(f"\n[Step 5] ✅ 로고 후보(이미지 포함) 생성 완료")

    # 8. Brand Consulting Report 생성
    print("\n[Step 5] Brand Consulting Report 생성 중...")
    try:
        report_context = {
            "diagnosis": diagnosis_context,
            "naming": naming_context,
            "concept": concept_context,
            "story": story_context,
            "logo_concepts": [c['output']['logo_concept'] for c in candidates]
        }
        
        report_prompt = f"""
        [Brand Consulting Results]
        {json.dumps(report_context, ensure_ascii=False, indent=2)}
        
        [Task]
        Create a comprehensive Brand Consulting Report in Korean.
        Include:
        1. overall_analysis (종합 분석)
        2. strengths (강점 5가지)
        3. weaknesses (약점 5가지)
        4. future_direction (향후 제언)
        5. recommendations (추천 사항 5가지)
        
        Output JSON: {{
            "overall_analysis": "...",
            "strengths": [...],
            "weaknesses": [...],
            "future_direction": "...",
            "recommendations": [...]
        }}
        """
        
        resp_report = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a Senior Brand Consultant."},
                {"role": "user", "content": report_prompt}
            ],
            response_format={"type": "json_object"}
        )
        report_data = json.loads(resp_report.choices[0].message.content)
        state["brand_consulting_report"] = report_data
        print("[Step 5] ✅ Report 생성 완료")
    except Exception as e:
        print(f"[Step 5] Report 생성 실패: {e}")
        state["brand_consulting_report"] = {}

    print(f"{'='*60}\n")
    return state
