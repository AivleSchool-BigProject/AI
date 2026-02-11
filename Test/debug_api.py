import requests
import json
import sys
import time
import os

# 공통 설정
BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

# Context 저장을 위한 변수들
diagnosis_context = {}
naming_context = {}
concept_context = {}
story_context = {}

# 자동으로 다음 brand 번호 찾기
def get_next_brand_folder():
    """Test/outputs/ 폴더에서 다음 brand 번호를 찾아 반환"""
    outputs_dir = os.path.join("Test", "outputs")
    os.makedirs(outputs_dir, exist_ok=True)
    
    # 기존 brand 폴더들 찾기
    existing_brands = []
    for folder in os.listdir(outputs_dir):
        if folder.startswith("brand_") and os.path.isdir(os.path.join(outputs_dir, folder)):
            try:
                num = int(folder.split("_")[1])
                existing_brands.append(num)
            except:
                pass
    
    # 다음 번호 결정
    next_num = max(existing_brands) + 1 if existing_brands else 1
    return f"brand_{next_num:02d}"  # brand_01, brand_02, ...

CURRENT_BRAND_FOLDER = get_next_brand_folder()
print(f"\n📁 저장 폴더: Test/outputs/{CURRENT_BRAND_FOLDER}\n")

def save_result(step_num, step_name, data):
    """결과를 파일로 저장"""
    base_dir = os.path.join("Test", "outputs", CURRENT_BRAND_FOLDER)
    os.makedirs(base_dir, exist_ok=True)
    
    # 각 단계별 파일명
    file_name = f"{step_name}.json"
    file_path = os.path.join(base_dir, file_name)
    
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
        if "brand_name" in cand:
            label = cand["brand_name"]
        elif "concept_statement" in cand:
            label = cand["concept_statement"][:40] + "..."
        elif "brand_story" in cand:
            label = cand["brand_story"][:40] + "..."
        else:
            label = f"후보 {i}"
        
        print(f"  {i}. {label}")
        
    while True:
        try:
            choice = input(f"\n👉 마음에 드는 {step_name} 번호를 입력하세요 (0~2): ")
            idx = int(choice)
            if 0 <= idx < len(candidates):
                print(f"✅ {idx}번 후보가 선택되었습니다.")
                return candidates[idx]
            else:
                print("❌ 0~2 사이의 숫자를 입력해주세요.")
        except ValueError:
            print("❌ 숫자를 입력해주세요.")

# =================================================================
# [Step 1] 진단 (Diagnosis)
# =================================================================
print_step_header("1. Diagnosis")

# answers.json 로드
try:
    file_path = r"C:/Users/User/Desktop/workspace/AI/LangGraph/answers.json"
    with open(file_path, "r", encoding="utf-8") as f:
        answers_data = json.load(f)
    step1_data = answers_data.get("step_1", {})
except FileNotFoundError:
    print(f"❌ '{file_path}' 파일을 찾을 수 없습니다.")
    sys.exit()

step1_payload = {
    "user_input": step1_data
}

try:
    url = f"{BASE_URL}/step1/diagnosis"
    print(f"📡 Step 1 요청 중... ({url})")
    resp = requests.post(url, json=step1_payload, headers=HEADERS)
    
    if resp.status_code == 200:
        print("✅ Step 1 성공!")
        response_data = resp.json()
        
        result = response_data.get("result", {})
        diagnosis_context = response_data.get("state_context", {})
        
        print(f" - Summary: {result.get('summary', '')[:50]}...")
        print(f" - Keywords: {diagnosis_context.get('keywords', [])}")
        
        save_result(1, "diagnosis", response_data)
        
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

step2_data = answers_data.get("step_2", {})

step2_payload = {
    "user_input": step2_data,
    "context": {
        "interview": diagnosis_context
    }
}

try:
    url = f"{BASE_URL}/step2/naming"
    print(f"📡 Step 2 요청 중... ({url})")
    resp = requests.post(url, json=step2_payload, headers=HEADERS)
    
    if resp.status_code == 200:
        print("✅ Step 2 성공!")
        response_data = resp.json()
        
        result = response_data.get("result", {})
        state_context = response_data.get("state_context", {})
        
        print(f" - Name 1: {result.get('name1')}")
        print(f" - Name 2: {result.get('name2')}")
        print(f" - Name 3: {result.get('name3')}")
        
        save_result(2, "naming", response_data)
        
        # 사용자 선택 (선택된 후보 상세 정보 반환)
        naming_candidates = state_context.get("candidates", [])
        naming_context = user_select_candidate(naming_candidates, "Naming")
        
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

step3_data = answers_data.get("step_3", {})

step3_payload = {
    "user_input": step3_data,
    "context": {
        "interview": diagnosis_context,
        "naming": naming_context  # 선택된 네이밍 상세 정보
    }
}

try:
    url = f"{BASE_URL}/step3/concept"
    print(f"📡 Step 3 요청 중... ({url})")
    resp = requests.post(url, json=step3_payload, headers=HEADERS)
    
    if resp.status_code == 200:
        print("✅ Step 3 성공!")
        response_data = resp.json()
        
        result = response_data.get("result", {})
        state_context = response_data.get("state_context", {})
        
        print(f" - Concept 1: {result.get('concept1', '')[:30]}...")
        print(f" - Concept 2: {result.get('concept2', '')[:30]}...")
        print(f" - Concept 3: {result.get('concept3', '')[:30]}...")
        
        save_result(3, "concept", response_data)
        
        # 사용자 선택
        concept_candidates = state_context.get("candidates", [])
        concept_context = user_select_candidate(concept_candidates, "Concept")
        
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

step4_data = answers_data.get("step_4", {})

step4_payload = {
    "user_input": step4_data,
    "context": {
        "interview": diagnosis_context,
        "naming": naming_context,
        "concept": concept_context  # 선택된 컨셉 상세 정보
    }
}

try:
    url = f"{BASE_URL}/step4/story"
    print(f"📡 Step 4 요청 중... ({url})")
    resp = requests.post(url, json=step4_payload, headers=HEADERS)
    
    if resp.status_code == 200:
        print("✅ Step 4 성공!")
        response_data = resp.json()
        
        result = response_data.get("result", {})
        state_context = response_data.get("state_context", {})
        
        print(f" - Story 1: {result.get('story1', '')[:30]}...")
        print(f" - Story 2: {result.get('story2', '')[:30]}...")
        print(f" - Story 3: {result.get('story3', '')[:30]}...")
        
        save_result(4, "story", response_data)
        
        # 사용자 선택
        story_candidates = state_context.get("candidates", [])
        story_context = user_select_candidate(story_candidates, "Story")
        
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

step5_data = answers_data.get("step_5", {})

step5_payload = {
    "user_input": step5_data,
    "context": {
        "interview": diagnosis_context,
        "naming": naming_context,
        "concept": concept_context,
        "story": story_context  # 선택된 스토리 상세 정보
    }
}

try:
    url = f"{BASE_URL}/step5/logo"
    print(f"📡 Step 5 요청 중... ({url})")
    resp = requests.post(url, json=step5_payload, headers=HEADERS)
    
    if resp.status_code == 200:
        print("✅ Step 5 성공!")
        response_data = resp.json()
        
        result = response_data.get("result", {})
        state_context = response_data.get("state_context", {})
        
        print("\n[생성된 로고 이미지 URL]")
        print(f" 🖼️  1. {result.get('logo1_url')}")
        print(f" 🖼️  2. {result.get('logo2_url')}")
        print(f" 🖼️  3. {result.get('logo3_url')}")
        
        save_result(5, "logo", response_data)
        
        # 로고 선택 (사용자)
        logo_candidates = state_context.get("candidates", [])
        logo_context = user_select_candidate(logo_candidates, "Logo")
            
    else:
        print(f"❌ Step 5 실패: {resp.text}")
        sys.exit()

except Exception as e:
    print(f"❌ Step 5 에러: {e}")
    sys.exit()

# =================================================================
# [최종] 선택된 Context 저장 (마케팅 단계용)
# =================================================================
print("\n" + "=" * 60)
print("💾 선택된 Context 저장 중...")
print("=" * 60)

# 선택된 정보로 마케팅용 context 구성
marketing_context = {
    "brand_name": naming_context.get("brand_name", ""),
    "concept_statement": concept_context.get("concept_statement", ""),
    "brand_story": story_context.get("brand_story", ""),
    "core_keywords": diagnosis_context.get("keywords", []),
    "target_persona": diagnosis_context.get("target_persona", "")
}

# selected_context.json 파일로 저장
context_file = os.path.join("Test", "outputs", CURRENT_BRAND_FOLDER, "selected_context.json")
with open(context_file, "w", encoding="utf-8") as f:
    json.dump(marketing_context, f, indent=2, ensure_ascii=False)

print(f"✅ 선택된 Context 저장 완료: {context_file}")
print("\n[저장된 내용]")
print(f"   - Brand: {marketing_context['brand_name']}")
print(f"   - Concept: {marketing_context['concept_statement'][:50]}...")
print(f"   - Story: {marketing_context['brand_story'][:50]}...")
print(f"   - Keywords: {marketing_context['core_keywords']}")
print(f"   - Persona: {marketing_context['target_persona']}")
print(f"   - Colors: {marketing_context['logo_color_palette']}")

print("\n" + "=" * 60)
print("✅ 전체 테스트 완료!")
print(f"📁 결과 폴더: Test/outputs/{CURRENT_BRAND_FOLDER}")
print(f"📄 마케팅용 Context: {context_file}")
print("=" * 60)
