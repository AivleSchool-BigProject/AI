"""
유틸리티 함수
JSON 로드, 프롬프트 관리, 컨텍스트 처리 등
"""
import json
import os
from typing import Dict, Any, List, Optional
from openai import OpenAI


def load_questions(step_num: int) -> List[Dict[str, Any]]:
    """
    질문 데이터 로드
    
    Args:
        step_num: 단계 번호 (1~9)
    
    Returns:
        해당 단계의 질문 리스트
    """
    # 1~5단계: questions.json
    # 6~9단계: marketing.json
    if 1 <= step_num <= 5:
        file_path = "questions.json"
        step_key = f"step_{step_num}"
    elif 6 <= step_num <= 9:
        file_path = "marketing.json"
        step_key = f"step_{step_num}"
    else:
        raise ValueError(f"잘못된 단계 번호: {step_num}")
    
    # 파일 로드
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"질문 파일을 찾을 수 없습니다: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data.get(step_key, [])


def get_openai_client() -> OpenAI:
    """OpenAI 클라이언트 생성"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
    return OpenAI(api_key=api_key)


def extract_answer_value(answers: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    questions.json 구조에서 value만 추출
    
    Args:
        answers: 사용자 답변 딕셔너리
        key: 질문 ID
        default: 기본값
    
    Returns:
        추출된 값
    """
    item = answers.get(key)
    if not item:
        return default
    
    # {"value": ...} 구조인 경우
    if isinstance(item, dict) and "value" in item:
        return item["value"]
    
    # 직접 값인 경우
    return item


def format_context_for_prompt(context: Dict[str, Any]) -> str:
    """
    누적 컨텍스트를 프롬프트용 문자열로 변환
    
    Args:
        context: 누적 컨텍스트
    
    Returns:
        포맷팅된 문자열
    """
    formatted = []
    
    for key, value in context.items():
        if key in ["brand_id", "user_id"]:
            continue
        
        if isinstance(value, dict):
            formatted.append(f"## {key}")
            formatted.append(json.dumps(value, ensure_ascii=False, indent=2))
        elif isinstance(value, list):
            formatted.append(f"## {key}")
            formatted.append(json.dumps(value, ensure_ascii=False, indent=2))
        else:
            formatted.append(f"## {key}: {value}")
    
    return "\n\n".join(formatted)


def download_image(url: str, save_path: str) -> bool:
    """
    이미지 다운로드
    
    Args:
        url: 이미지 URL
        save_path: 저장 경로
    
    Returns:
        성공 여부
    """
    import requests
    
    try:
        response = requests.get(url, stream=True, timeout=30)
        if response.status_code == 200:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"[Image] 다운로드 완료: {save_path}")
            return True
        else:
            print(f"[Image] 다운로드 실패 (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"[Image] 다운로드 오류: {e}")
        return False


def validate_step_input(step_num: int, user_input: Dict[str, Any]) -> bool:
    """
    사용자 입력 검증
    
    Args:
        step_num: 단계 번호
        user_input: 사용자 입력
    
    Returns:
        검증 성공 여부
    """
    if not user_input or "answers" not in user_input:
        print(f"[Validation] Step {step_num} 입력 데이터가 없습니다.")
        return False
    
    # 추가 검증 로직 (필요 시)
    # 예: 필수 질문 답변 확인
    
    return True
