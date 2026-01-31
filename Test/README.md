# Step 1 Diagnosis 실험

Step 1 초기 진단 단계의 질문-답변 분석 실험입니다.

## 📁 파일 구조

```
Test/
├── test.json              # Step 1 질문 데이터 (7개 질문)
├── sample_answers.json    # 테스트용 답변 데이터
├── test_diagnosis.py      # 분석 스크립트
└── README.md             # 이 파일
```

## 🚀 실행 방법

```bash
cd "c:\Users\User\Desktop\개발 파일\Test"
python test_diagnosis.py
```

## 📊 출력 결과

실행하면 `output_test/` 폴더에 **두 가지 파일**이 생성됩니다:

### 1️⃣ `user_diagnosis.json` (사용자용 - DB 저장)
사용자에게 보여줄 진단 결과 **요약 + 분석**

```json
{
    "summary": "비즈니스를 한 문장으로 요약",
    "keywords": ["키워드1", "키워드2", "키워드3", "키워드4", "키워드5"],
    "analysis": "타겟, 시장, 브랜드 방향성을 통합한 핵심 분석 (300자 이내)",
    "key_insights": "핵심 인사이트 및 제안사항 (3-4문장)"
}
```

### 2️⃣ `rag_context.json` (RAG용 - 누적 컨텍스트)
다음 단계(Step 2 네이밍)에서 참조할 **분석 데이터 + 원본 답변**

```json
{
    "step_1_analysis": {
        "summary": "비즈니스 요약",
        "keywords": ["키워드1", "키워드2", ...],
        "analysis": "통합 분석 (300자 이내)",
        "key_insights": "핵심 인사이트"
    },
    "step_1_raw_answers": {
        "service_definition": "...",
        "pain_point": "...",
        "target_persona": "...",
        "usp": "...",
        "growth_stage": "...",
        "industry": "...",
        "vision": "..."
    }
}
```

## 🔑 핵심 개념

### 사용자용 vs RAG용
- **사용자용**: 고객에게 보여줄 간결한 진단 결과 (UI/DB 저장)
- **RAG용**: AI가 다음 단계에서 참조할 상세 컨텍스트 (누적 저장)

### 누적 컨텍스트 (Cumulative Context)
Step 2, 3, 4... 각 단계에서 이전 단계의 `rag_context.json`을 읽어서
더 정확한 브랜드 컨설팅 결과를 생성합니다.

## 📝 답변 데이터 수정

`sample_answers.json`을 수정하여 다른 비즈니스로 테스트할 수 있습니다:

```json
{
    "s1_one_line_definition": "여기에 서비스 정의",
    "s1_core_problem": "여기에 고객 문제점",
    "s1_target_persona": {
        "value": "Early Stage Startup CEO"
    },
    ...
}
```

## ⚙️ 필요 패키지

```bash
pip install openai
```
