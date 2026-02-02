import requests
import json
import sys
import time

# 1. 파일 읽기
try:
    with open("sample_answers.json", "r", encoding="utf-8") as f:
        answers_data = json.load(f)
except FileNotFoundError:
    print("❌ 'sample_answers.json' 파일을 찾을 수 없습니다.")
    sys.exit()

# 공통 설정
BASE_URL = "http://localhost:8000/api/v1/brand"
HEADERS = {"Content-Type": "application/json"}
USER_ID = "debug_user_01"

import os

# Context 저장을 위한 변수들
diagnosis_context = {}
naming_context = {}
concept_context = {}
story_context = {}

CURRENT_BRAND_ID = f"debug_test_{int(time.time())}"

def save_result(step_num, step_name, data):
    """결과를 파일로 저장"""
    base_dir = os.path.join("Test", "outputs", CURRENT_BRAND_ID)
    step_dir = os.path.join(base_dir, f"step_{step_num}_{step_name}")
    os.makedirs(step_dir, exist_ok=True)
    
    file_path = os.path.join(step_dir, "result.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"   💾 결과 저장됨: {file_path}")

def print_step_header(step_name):
    print("\n" + "=" * 60)
    print(f"▶️ [Step {step_name}] API 요청 테스트")
    print("=" * 60)

def user_select_candidate(candidates, step_name):
    """사용자가 후보 중 하나를 선택하게 함"""
    print(f"\n[👀 {step_name} 후보 선택]")
    for i, cand in enumerate(candidates):
        output = cand["output"]
        # 출력 필드는 Step마다 다를 수 있음
        label = ""
        if "brand_name" in output: label = output["brand_name"]
        elif "concept_statement" in output: label = output["concept_statement"][:30] + "..."
        elif "brand_story" in output: label = output["brand_story"][:30] + "..."
        elif "logo_image_url" in output: label = output["logo_image_url"][:50] + "..."
        
        print(f"  {i+1}. {label}")
        
    while True:
        try:
            choice = input(f"\n👉 마음에 드는 {step_name} 번호를 입력하세요 (1~3): ")
            idx = int(choice) - 1
            if 0 <= idx < len(candidates):
                print(f"✅ {idx+1}번 후보가 선택되었습니다.")
                return candidates[idx]["output"]
            else:
                print("❌ 1~3 사이의 숫자를 입력해주세요.")
        except ValueError:
            print("❌ 숫자를 입력해주세요.")

# =================================================================
# [Step 1] 진단 (Diagnosis)
# =================================================================
print_step_header("1. Diagnosis")

step1_payload = {
    "user_id": USER_ID,
    "qa_answers": answers_data
}

try:
    url = f"{BASE_URL}/step1/diagnosis"
    print(f"📡 Step 1 요청 중... ({url})")
    resp = requests.post(url, json=step1_payload, headers=HEADERS)
    
    if resp.status_code == 200:
        print("✅ Step 1 성공!")
        result = resp.json()
        
        # Brand ID 업데이트 (서버에서 받은게 있으면 사용, 없으면 시간기반 유지)
        if result.get("brand_id"):
            CURRENT_BRAND_ID = result.get("brand_id")
            
        analysis = result.get("analysis", {})
        
        diagnosis_context = {
            "diagnosis_summary": analysis.get("summary", ""),
            "core_keywords": analysis.get("keywords", []),
            "target_persona": analysis.get("persona", ""),
            "perspectives": analysis.get("perspectives", {})
        }
        print(f" - Summary: {analysis.get('summary')[:50]}...")
        
        # 저장
        save_result(1, "diagnosis", result)
        
    else:
        print(f"❌ Step 1 실패: {resp.text}")
        sys.exit()

except Exception as e:
    print(f"❌ Step 1 에러: {e}")
    sys.exit()

# =================================================================
# [Step 2] 네이밍 (Naming)
# =================================================================
print_step_header("2. Naming")

step2_qa = {
    "preferred_language": "English",
    "naming_style": "Modern & Simple"
}

step2_payload = {
    "user_id": USER_ID,
    "diagnosis_context": diagnosis_context,
    "qa_answers": step2_qa
}

selected_naming = None

try:
    url = f"{BASE_URL}/step2/naming"
    print(f"📡 Step 2 요청 중... ({url})")
    resp = requests.post(url, json=step2_payload, headers=HEADERS)
    
    if resp.status_code == 200:
        print("✅ Step 2 성공!")
        result = resp.json()
        
        save_result(2, "naming", result)
        
        candidates = result.get("candidates", [])
        
        # [사용자 선택]
        selected_naming = user_select_candidate(candidates, "Naming")
        
        # 선택된 결과로 Context 구성
        naming_context = {
            "brand_name": selected_naming["brand_name"],
            "name_rationale": selected_naming["name_rationale"],
            "selected_criteria": ["Modern", "Global"] 
        }
    else:
        print(f"❌ Step 2 실패: {resp.text}")
        sys.exit()

except Exception as e:
    print(f"❌ Step 2 에러: {e}")
    sys.exit()

# =================================================================
# [Step 3] 컨셉 (Concept)
# =================================================================
print_step_header("3. Concept")

step3_qa = {
    "concept_direction": "Future-oriented",
    "tone_and_manner": "Professional"
}

step3_payload = {
    "user_id": USER_ID,
    "diagnosis_context": diagnosis_context,
    "naming_context": naming_context,
    "qa_answers": step3_qa
}

selected_concept = None

try:
    url = f"{BASE_URL}/step3/concept"
    print(f"📡 Step 3 요청 중... ({url})")
    resp = requests.post(url, json=step3_payload, headers=HEADERS)
    
    if resp.status_code == 200:
        print("✅ Step 3 성공!")
        result = resp.json()
        
        save_result(3, "concept", result)
        
        candidates = result.get("candidates", [])
        
        # [사용자 선택]
        selected_concept = user_select_candidate(candidates, "Concept")
        
        # Context 구성
        concept_context = {
            "concept_statement": selected_concept.get("concept_statement"),
            "concept_rationale": selected_concept.get("concept_rationale")
        }
    else:
        print(f"❌ Step 3 실패: {resp.text}")
        sys.exit()

except Exception as e:
    print(f"❌ Step 3 에러: {e}")
    sys.exit()

# =================================================================
# [Step 4] 스토리 (Story)
# =================================================================
print_step_header("4. Story")

step4_qa = {
    "story_theme": "Innovation & Growth"
}

step4_payload = {
    "user_id": USER_ID,
    "diagnosis_context": diagnosis_context,
    "naming_context": naming_context,
    "concept_context": concept_context,
    "qa_answers": step4_qa
}

selected_story = None

try:
    url = f"{BASE_URL}/step4/story"
    print(f"📡 Step 4 요청 중... ({url})")
    resp = requests.post(url, json=step4_payload, headers=HEADERS)
    
    if resp.status_code == 200:
        print("✅ Step 4 성공!")
        result = resp.json()
        
        save_result(4, "story", result)
        
        candidates = result.get("candidates", [])
        
        # [사용자 선택]
        selected_story = user_select_candidate(candidates, "Story")
        
        story_context = {
            "brand_story": selected_story.get("brand_story"),
            "story_rationale": selected_story.get("story_rationale")
        }
    else:
        print(f"❌ Step 4 실패: {resp.text}")
        sys.exit()

except Exception as e:
    print(f"❌ Step 4 에러: {e}")
    sys.exit()

# =================================================================
# [Step 5] 로고 (Logo)
# =================================================================
print_step_header("5. Logo (DALL-E 3)")
print("⚠️ 이미지 생성은 시간이 조금 더 걸릴 수 있습니다 (15초 이상)")

step5_qa = {
    "logo_style": "Minimalist",
    "color_preference": "Blue & White"
}

step5_payload = {
    "user_id": USER_ID,
    "diagnosis_context": diagnosis_context,
    "naming_context": naming_context,
    "concept_context": concept_context,
    "story_context": story_context,
    "qa_answers": step5_qa
}

try:
    url = f"{BASE_URL}/step5/logo"
    print(f"📡 Step 5 요청 중... ({url})")
    resp = requests.post(url, json=step5_payload, headers=HEADERS)
    
    if resp.status_code == 200:
        print("✅ Step 5 성공!")
        result = resp.json()
        
        save_result(5, "logo", result)
        
        candidates = result.get("candidates", [])
        
        print("\n[생성된 로고 이미지 URL]")
        for i, cand in enumerate(candidates):
            output = cand["output"]
            print(f" 🖼️  {i+1}. {output.get('logo_image_url')}")
            
    else:
        print(f"❌ Step 5 실패: {resp.text}")

except Exception as e:
    print(f"❌ Step 5 에러: {e}")
