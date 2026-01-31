# Step 1 진단 분석 API - 간단 사용 가이드

## 🎯 핵심 개념

### 두 가지 출력 데이터

1. **user_diagnosis** (DB 저장 ✅)
   - 사용자에게 보여줄 Step 1 진단 결과
   - Spring에서 DB에 저장
   
2. **rag_context** (임시 데이터 ⏱️)
   - Step 2에서 사용할 컨텍스트
   - Redis 또는 메모리에 임시 저장
   - **DB에 저장하지 않음**

---

## 📡 API 호출 예시

### 요청
```bash
POST http://localhost:8000/api/v1/diagnosis/step1
Content-Type: application/json

{
  "s1_one_line_definition": "AI를 활용해서 브랜드 컨설팅을 자동화하는 서비스",
  "s1_core_problem": "브랜드 컨설팅 비용이 너무 비싸고...",
  ...
}
```

### 응답
```json
{
  "user_result": {
    "summary": "...",
    "keywords": [...],
    "analysis": "...",
    "key_insights": "..."
  },
  "rag_context": {
    "step_1_analysis": {...},
    "step_1_raw_answers": {...}
  }
}
```

---

## 💾 Spring에서 처리

```java
// 1. API 호출
DiagnosisResponse response = fastApiClient.analyzeStep1(request);

// 2. user_result → DB 저장
diagnosisRepository.save(response.getUserResult());

// 3. rag_context → Redis 임시 저장
redisTemplate.opsForValue().set(
    "rag:" + sessionId, 
    response.getRagContext()
);
```

---

## 🔄 다음 단계 (Step 2)

Step 2 호출 시 Step 1의 `rag_context`를 함께 전달:

```java
// Redis에서 가져오기
RagContext step1Context = redisTemplate.opsForValue().get("rag:" + sessionId);

// Step 2 호출
Step2Response step2 = fastApiClient.analyzeStep2(userAnswers, step1Context);
```

---

## ✅ 체크리스트

- [x] user_diagnosis는 DB에 저장
- [x] rag_context는 Redis에 임시 저장 (DB X)
- [ ] Step 2-8 순차 진행
- [ ] Step 8 완료 후 최종 리포트 생성
- [ ] 최종 리포트만 DB에 저장
