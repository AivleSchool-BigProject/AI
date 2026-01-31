"""
Brand Consulting API Router
FE 요청을 받아 각 단계별 로직을 호출하고 응답을 반환
현재는 구조 검증을 위해 DUMMY DATA를 반환합니다.
"""
from fastapi import APIRouter, HTTPException, Path, Body
from api.schemas.request import (
    DiagnosisRequest, NamingRequest, ConceptRequest, StoryRequest, LogoRequest, RegenerateRequest
)
from api.schemas.response import (
    DiagnosisResponse, GenerationResponse, CandidateItem
)
import uuid

router = APIRouter()

# =================================================================
# 1. Diagnosis (Step 1)
# =================================================================
@router.post("/step1/diagnosis", response_model=DiagnosisResponse)
async def create_diagnosis(request: DiagnosisRequest):
    """
    Step 1: 진단 (Diagnosis)
    Q&A 입력을 받아 브랜드 상세 진단을 수행합니다. (후보 없음)
    """
    # TODO: LangGraph Node 호출 연결 (현재는 더미)
    
    return DiagnosisResponse(
        brand_id="test-brand-id",
        step=1,
        analysis={
            "summary": "이 브랜드는 MZ세대를 타겟으로 하는 친환경 아웃도어 의류 브랜드입니다.",
            "keywords": ["Eco-friendly", "Sustainable", "Trendy"],
            "persona": "가치 소비를 지향하는 2030 등산객",
            "perspectives": {
                "business_perspective": "구독 모델 도입 가능성 높음",
                "user_perspective": "디자인과 기능성 모두 중시",
                "market_perspective": "친환경 아웃도어 시장 성장세"
            }
        }
    )

# =================================================================
# 2. Naming (Step 2)
# =================================================================
@router.post("/step2/naming", response_model=GenerationResponse)
async def create_naming(request: NamingRequest):
    """
    Step 2: 네이밍 (Naming)
    Diagnosis 결과와 함께 호출하여 3개의 브랜드명 후보를 생성합니다.
    """
    # TODO: LangGraph Node 호출 (Naming Node)
    
    return GenerationResponse(
        brand_id="test-brand-id",
        step=2,
        candidates=[
            CandidateItem(id=0, output={"brand_name": "EcoPeak", "name_rationale": "Eco와 Peak의 합성어"}),
            CandidateItem(id=1, output={"brand_name": "GreenTrek", "name_rationale": "녹색 여행을 의미"}),
            CandidateItem(id=2, output={"brand_name": "NatureWalk", "name_rationale": "자연을 걷다는 의미"})
        ]
    )

# =================================================================
# 3. Concept (Step 3)
# =================================================================
@router.post("/step3/concept", response_model=GenerationResponse)
async def create_concept(request: ConceptRequest):
    """
    Step 3: 컨셉 (Concept)
    Naming 확정 Context와 함께 호출하여 3개의 컨셉 후보를 생성합니다.
    """
    # TODO: LangGraph Node 호출
    
    return GenerationResponse(
        brand_id="test-brand-id",
        step=3,
        candidates=[
            CandidateItem(id=0, output={"concept_statement": "자연과 하나되는 삶", "concept_rationale": "일체감 강조"}),
            CandidateItem(id=1, output={"concept_statement": "내일의 지구를 위한 발걸음", "concept_rationale": "미래 지향적"}),
            CandidateItem(id=2, output={"concept_statement": "스타일, 그 이상의 가치", "concept_rationale": "가치 소비 강조"})
        ]
    )

# =================================================================
# 4. Story (Step 4)
# =================================================================
@router.post("/step4/story", response_model=GenerationResponse)
async def create_story(request: StoryRequest):
    """
    Step 4: 스토리 (Story)
    Step 1~3 Context와 함께 호출하여 3개의 스토리 후보를 생성합니다.
    """
    # TODO: LangGraph Node 호출
    
    return GenerationResponse(
        brand_id="test-brand-id",
        step=4,
        candidates=[
            CandidateItem(id=0, output={"brand_story": "산 정상에서 마시는 커피 한 잔...", "story_rationale": "감성적 접근"}),
            CandidateItem(id=1, output={"brand_story": "우리는 플라스틱 없는 세상을 꿈꿉니다...", "story_rationale": "미션 중심"}),
            CandidateItem(id=2, output={"brand_story": "당신의 모험에 날개를 달아드립니다...", "story_rationale": "기능적 혜택 강조"})
        ]
    )

# =================================================================
# 5. Logo (Step 5)
# =================================================================
@router.post("/step5/logo", response_model=GenerationResponse)
async def create_logo(request: LogoRequest):
    """
    Step 5: 로고 (Logo)
    모든 데이터 Context와 함께 호출하여 3개의 로고 이미지 후보를 생성합니다.
    """
    # TODO: LangGraph Node 호출 (DALL-E 3)
    
    return GenerationResponse(
        brand_id="test-brand-id",
        step=5,
        candidates=[
            CandidateItem(id=0, output={"logo_image_url": "http://example.com/logo1.png", "logo_concept": "심플한 심볼형"}),
            CandidateItem(id=1, output={"logo_image_url": "http://example.com/logo2.png", "logo_concept": "워드마크형"}),
            CandidateItem(id=2, output={"logo_image_url": "http://example.com/logo3.png", "logo_concept": "엠블럼형"})
        ]
    )

# =================================================================
# [Regeneration]
# =================================================================
@router.post("/regenerate", response_model=GenerationResponse)
async def regenerate_step(request: RegenerateRequest):
    """
    재생성 (Regenerate)
    특정 단계의 결과가 만족스럽지 않을 때, 피드백을 반영하여 다시 생성합니다.
    """
    # TODO: LangGraph 재생성 로직 연결
    step = request.step
    
    print(f"[Regenerate] Step {step} 피드백 반영: {request.feedback}")
    
    # 더미 응답 (Step에 따라 다르게 줄 수도 있음)
    return GenerationResponse(
        brand_id="test-brand-id",
        step=step,
        candidates=[
            CandidateItem(id=0, output={"result": "재생성된 후보 1", "rationale": f"피드백 반영: {request.feedback}"}),
            CandidateItem(id=1, output={"result": "재생성된 후보 2", "rationale": "다양한 변주"}),
            CandidateItem(id=2, output={"result": "재생성된 후보 3", "rationale": "새로운 시도"})
        ]
    )
