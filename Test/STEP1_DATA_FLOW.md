# Step 1 진단 분석 - 데이터 흐름 가이드

## 📊 데이터 구조

### 1. user_diagnosis (DB 저장용)
**용도**: 사용자에게 보여줄 Step 1 진단 결과  
**저장 위치**: Spring → Database  
**구조**:
```json
{
    "summary": "비즈니스 한 줄 요약",
    "keywords": ["키워드1", "키워드2", ...],
    "analysis": "통합 분석 (300자 이내)",
    "key_insights": "핵심 인사이트"
}
```

### 2. rag_context (임시 데이터)
**용도**: Step 2 네이밍 분석 시 참조할 컨텍스트  
**저장 위치**: 메모리 또는 Redis (임시)  
**DB 저장**: ❌ 저장하지 않음  
**구조**:
```json
{
    "step_1_analysis": {
        "summary": "...",
        "keywords": [...],
        "analysis": "...",
        "key_insights": "..."
    },
    "step_1_raw_answers": {
        "service_definition": "...",
        "pain_point": "...",
        ...
    }
}
```

---

## 🔄 전체 워크플로우

### Step 1 → Step 2 → ... → Step 8
```
Step 1 답변
    ↓
[FastAPI 분석]
    ↓
┌─────────────────────┬──────────────────────┐
│  user_diagnosis_1   │   rag_context_1      │
│  (DB에 저장)        │   (메모리/Redis)     │
└─────────────────────┴──────────────────────┘
                              ↓
                       [Step 2로 전달]
                              ↓
                       [Step 2 분석]
                              ↓
                    ┌─────────────────────┬──────────────────────┐
                    │  user_diagnosis_2   │   rag_context_2      │
                    │  (DB에 저장)        │   (누적)             │
                    └─────────────────────┴──────────────────────┘
                                                  ↓
                                           [Step 3로 전달]
                                                  ↓
                                                 ...
                                                  ↓
                                           [Step 8 완료]
                                                  ↓
                                    [모든 RAG 데이터 종합]
                                                  ↓
                                         [최종 리포트 생성]
                                                  ↓
                                          [DB에 최종 저장]
```

---

## 💾 Spring에서 처리 방법

### Step 1 완료 시
```java
// 1. FastAPI 호출
DiagnosisResponse response = fastApiClient.analyzeStep1(userAnswers);

// 2. user_diagnosis만 DB에 저장
UserDiagnosis step1Result = response.getUserResult();
diagnosisRepository.save(step1Result);

// 3. rag_context는 Redis에 임시 저장 (또는 메모리)
String sessionId = user.getSessionId();
redisTemplate.opsForValue().set(
    "rag_context:" + sessionId, 
    response.getRagContext(),
    Duration.ofHours(24)  // 24시간 후 자동 삭제
);
```

### Step 2 호출 시
```java
// 1. Redis에서 Step 1 RAG 컨텍스트 가져오기
RagContext step1Context = redisTemplate.opsForValue().get("rag_context:" + sessionId);

// 2. Step 2 API 호출 시 함께 전달
Step2Request request = new Step2Request(
    userAnswers,
    step1Context  // Step 1 컨텍스트 포함
);

Step2Response response = fastApiClient.analyzeStep2(request);

// 3. user_diagnosis_2 DB 저장
diagnosisRepository.save(response.getUserResult());

// 4. rag_context_2 Redis 업데이트 (누적)
RagContext combinedContext = combineContexts(step1Context, response.getRagContext());
redisTemplate.opsForValue().set("rag_context:" + sessionId, combinedContext);
```

### Step 8 완료 후 최종 리포트
```java
// 1. 모든 RAG 컨텍스트 가져오기
RagContext fullContext = redisTemplate.opsForValue().get("rag_context:" + sessionId);

// 2. 최종 리포트 생성 API 호출
FinalReportResponse finalReport = fastApiClient.generateFinalReport(fullContext);

// 3. 최종 리포트만 DB에 저장
finalReportRepository.save(finalReport);

// 4. Redis 데이터 삭제 (더 이상 필요 없음)
redisTemplate.delete("rag_context:" + sessionId);
```

---

## 🎯 핵심 포인트

1. **user_diagnosis**: 각 단계별로 DB에 저장 (사용자에게 보여줄 결과)
2. **rag_context**: 임시 저장 (다음 단계 입력용, DB 저장 X)
3. **최종 리포트**: Step 8 완료 후 모든 RAG 누적 데이터로 생성 → DB 저장

---

## 📝 데이터베이스 스키마 예시

### user_diagnosis 테이블
```sql
CREATE TABLE user_diagnosis (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    step_number INT NOT NULL,  -- 1, 2, 3, ..., 8
    summary TEXT,
    keywords JSON,
    analysis TEXT,
    key_insights TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### final_report 테이블
```sql
CREATE TABLE final_report (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    full_summary TEXT,
    brand_strategy TEXT,
    marketing_plan TEXT,
    visual_assets JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔑 Redis 키 구조

```
rag_context:{session_id}
```

**TTL**: 24시간 (Step 8 완료 전까지만 유지)
