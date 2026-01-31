"""
Step 1 Diagnosis 실험 스크립트
질문-답변 데이터를 분석하여 두 가지 출력물을 생성합니다:
1. 사용자용 (DB 저장): 진단 결과 요약
2. RAG용 (누적 컨텍스트): 다음 단계에서 참조할 분석 데이터
"""

import json
import os
from openai import OpenAI
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"✅ {filepath}")

def get_answer_value(answers, key):
    """답변에서 value 추출"""
    item = answers.get(key)
    if isinstance(item, dict) and "value" in item:
        return item["value"]
    return item

def analyze_diagnosis(questions, answers):
    """
    질문-답변을 분석하여 요약/분석 리포트 생성
    """
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    # Q&A 텍스트 생성
    qa_text = ""
    for q in questions:
        q_id = q["id"]
        answer = get_answer_value(answers, q_id)
        if answer:
            qa_text += f"Q: {q['question_text']}\nA: {answer}\n\n"
    
    # 프롬프트
    system_prompt = """당신은 브랜드 컨설팅 전문가입니다.
고객의 진단 답변을 분석하여 간결한 요약과 분석을 JSON으로 제공하세요.

출력 형식:
{
  "summary": "비즈니스를 한 문장으로 요약",
  "keywords": ["키워드1", "키워드2", "키워드3", "키워드4", "키워드5"],
  "analysis": "타겟, 시장, 브랜드 방향성을 통합한 핵심 분석 (300자 이내)",
  "key_insights": "핵심 인사이트 및 제안사항 (3-4문장)"
}"""

    user_prompt = f"다음 진단 답변을 분석해주세요:\n\n{qa_text}"
    
    print("🤖 AI 분석 중...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)

def main():
    print("=" * 60)
    print("Step 1 Diagnosis 실험")
    print("=" * 60)
    
    # 데이터 로드
    questions = load_json("test.json")["step_1"]
    answers = load_json("sample_answers.json")
    
    # AI 분석
    analysis = analyze_diagnosis(questions, answers)
    
    # 출력 디렉토리
    os.makedirs("output_test", exist_ok=True)
    
    # 1. 사용자용 (DB 저장) - 진단 결과 요약 + 분석
    user_result = {
        "summary": analysis["summary"],
        "analysis": analysis["analysis"],
        "key_insights": analysis["key_insights"]
    }
    save_json(user_result, "output_test/user_diagnosis.json")
    
    # 2. RAG용 (누적 컨텍스트) - 다음 단계에서 참조할 상세 데이터
    rag_context = {
        "step_1_analysis": {
            "summary": analysis["summary"],
            "keywords": analysis["keywords"],
            "analysis": analysis["analysis"],
            "key_insights": analysis["key_insights"]
        },
        "step_1_raw_answers": {
            "service_definition": get_answer_value(answers, "s1_one_line_definition"),
            "pain_point": get_answer_value(answers, "s1_core_problem"),
            "target_persona": get_answer_value(answers, "s1_target_persona"),
            "usp": get_answer_value(answers, "s1_differentiation"),
            "growth_stage": get_answer_value(answers, "s1_growth_stage"),
            "industry": get_answer_value(answers, "s1_industry"),
            "vision": get_answer_value(answers, "s1_vision")
        }
    }
    save_json(rag_context, "output_test/rag_context.json")
    
    # 결과 출력
    print("\n" + "=" * 60)
    print("📊 분석 결과")
    print("=" * 60)
    print(f"요약: {analysis['summary']}")
    print(f"키워드: {', '.join(analysis['keywords'])}")
    print(f"분석: {analysis['analysis']}")
    print(f"핵심 인사이트: {analysis['key_insights']}")
    print("\n✨ 완료!")

if __name__ == "__main__":
    main()
