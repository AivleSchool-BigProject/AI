# Spring → FastAPI 연동 가이드

## 📡 FastAPI 엔드포인트 정의

### POST `/api/v1/diagnosis/step1`

**URL**: `http://localhost:8000/api/v1/diagnosis/step1`

**요청 형식**:
```json
{
  "s1_one_line_definition": "서비스 정의 (문자열)",
  "s1_core_problem": "핵심 문제점 (문자열)",
  "s1_target_persona": {
    "id": "opt_startup_ceo",
    "text": "초기 스타트업 대표",
    "value": "Early Stage Startup CEO"
  },
  "s1_differentiation": "차별화 요소 (문자열)",
  "s1_growth_stage": {
    "id": "opt_mvp",
    "text": "MVP 개발 중",
    "value": "MVP Development"
  },
  "s1_industry": {
    "id": "opt_saas",
    "text": "SaaS/플랫폼",
    "value": "SaaS/Platform"
  },
  "s1_vision": "비전 (문자열)"
}
```

**응답 형식**:
```json
{
  "user_result": {
    "summary": "비즈니스 요약",
    "keywords": ["키워드1", "키워드2", ...],
    "analysis": "통합 분석",
    "key_insights": "핵심 인사이트"
  },
  "rag_context": {
    "step_1_analysis": { ... },
    "step_1_raw_answers": { ... }
  }
}
```

---

## 🔧 Spring 연동 코드

### 1. DTO 클래스 정의

```java
// DiagnosisRequest.java
@Data
@NoArgsConstructor
@AllArgsConstructor
public class DiagnosisRequest {
    private String s1_one_line_definition;
    private String s1_core_problem;
    private TargetPersona s1_target_persona;
    private String s1_differentiation;
    private GrowthStage s1_growth_stage;
    private Industry s1_industry;
    private String s1_vision;
}

@Data
@NoArgsConstructor
@AllArgsConstructor
class TargetPersona {
    private String id;
    private String text;
    private String value;
}

@Data
@NoArgsConstructor
@AllArgsConstructor
class GrowthStage {
    private String id;
    private String text;
    private String value;
}

@Data
@NoArgsConstructor
@AllArgsConstructor
class Industry {
    private String id;
    private String text;
    private String value;
}
```

```java
// DiagnosisResponse.java
@Data
@NoArgsConstructor
@AllArgsConstructor
public class DiagnosisResponse {
    private UserDiagnosisResult user_result;
    private RagContext rag_context;
}

@Data
@NoArgsConstructor
@AllArgsConstructor
class UserDiagnosisResult {
    private String summary;
    private List<String> keywords;
    private String analysis;
    private String key_insights;
}

@Data
@NoArgsConstructor
@AllArgsConstructor
class RagContext {
    private DiagnosisAnalysis step_1_analysis;
    private RawAnswers step_1_raw_answers;
}

@Data
@NoArgsConstructor
@AllArgsConstructor
class DiagnosisAnalysis {
    private String summary;
    private List<String> keywords;
    private String analysis;
    private String key_insights;
}

@Data
@NoArgsConstructor
@AllArgsConstructor
class RawAnswers {
    private String service_definition;
    private String pain_point;
    private String target_persona;
    private String usp;
    private String growth_stage;
    private String industry;
    private String vision;
}
```

---

### 2. Service 클래스

```java
@Service
public class BrandDiagnosisService {
    
    private final RestTemplate restTemplate;
    private final DiagnosisRepository diagnosisRepository;
    
    @Value("${fastapi.url:http://localhost:8000}")
    private String fastApiUrl;
    
    public BrandDiagnosisService(RestTemplate restTemplate, 
                                 DiagnosisRepository diagnosisRepository) {
        this.restTemplate = restTemplate;
        this.diagnosisRepository = diagnosisRepository;
    }
    
    /**
     * Step 1 진단 분석
     */
    public DiagnosisResponse analyzeStep1(DiagnosisRequest request, Long userId) {
        // 1. FastAPI 호출
        String url = fastApiUrl + "/api/v1/diagnosis/step1";
        
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        
        HttpEntity<DiagnosisRequest> entity = new HttpEntity<>(request, headers);
        
        ResponseEntity<DiagnosisResponse> response = restTemplate.postForEntity(
            url,
            entity,
            DiagnosisResponse.class
        );
        
        DiagnosisResponse result = response.getBody();
        
        // 2. user_result를 DB에 저장
        UserDiagnosis diagnosis = new UserDiagnosis();
        diagnosis.setUserId(userId);
        diagnosis.setStepNumber(1);
        diagnosis.setSummary(result.getUser_result().getSummary());
        diagnosis.setKeywords(result.getUser_result().getKeywords());
        diagnosis.setAnalysis(result.getUser_result().getAnalysis());
        diagnosis.setKeyInsights(result.getUser_result().getKey_insights());
        
        diagnosisRepository.save(diagnosis);
        
        // 3. rag_context는 Redis에 임시 저장 (또는 반환만)
        // redisTemplate.opsForValue().set("rag:" + sessionId, result.getRag_context());
        
        return result;
    }
}
```

---

### 3. Controller 클래스

```java
@RestController
@RequestMapping("/api/diagnosis")
public class DiagnosisController {
    
    private final BrandDiagnosisService diagnosisService;
    
    public DiagnosisController(BrandDiagnosisService diagnosisService) {
        this.diagnosisService = diagnosisService;
    }
    
    /**
     * Step 1 진단 분석 API
     */
    @PostMapping("/step1")
    public ResponseEntity<DiagnosisResponse> analyzeStep1(
            @RequestBody DiagnosisRequest request,
            @AuthenticationPrincipal UserDetails userDetails) {
        
        Long userId = getUserId(userDetails);
        
        DiagnosisResponse response = diagnosisService.analyzeStep1(request, userId);
        
        return ResponseEntity.ok(response);
    }
    
    private Long getUserId(UserDetails userDetails) {
        // 실제 사용자 ID 추출 로직
        return 1L;
    }
}
```

---

### 4. RestTemplate 설정

```java
@Configuration
public class RestTemplateConfig {
    
    @Bean
    public RestTemplate restTemplate() {
        RestTemplate restTemplate = new RestTemplate();
        
        // 타임아웃 설정
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(5000);  // 5초
        factory.setReadTimeout(10000);    // 10초
        
        restTemplate.setRequestFactory(factory);
        
        return restTemplate;
    }
}
```

---

## 🧪 테스트 방법

### Postman으로 Spring API 테스트

**URL**: `http://localhost:8080/api/diagnosis/step1`

**Method**: POST

**Headers**:
```
Content-Type: application/json
Authorization: Bearer {your-jwt-token}
```

**Body**:
```json
{
  "s1_one_line_definition": "AI를 활용해서 브랜드 컨설팅을 자동화하는 서비스",
  "s1_core_problem": "브랜드 컨설팅 비용이 너무 비싸고, 시간이 오래 걸려서 초기 스타트업이 접근하기 어렵다",
  "s1_target_persona": {
    "id": "opt_startup_ceo",
    "text": "초기 스타트업 대표",
    "value": "Early Stage Startup CEO"
  },
  "s1_differentiation": "AI 기반 자동화로 24시간 내에 전문가 수준의 브랜드 전략을 제공할 수 있다",
  "s1_growth_stage": {
    "id": "opt_mvp",
    "text": "MVP 개발 중",
    "value": "MVP Development"
  },
  "s1_industry": {
    "id": "opt_saas",
    "text": "SaaS/플랫폼",
    "value": "SaaS/Platform"
  },
  "s1_vision": "AI 브랜드 컨설팅으로 10만 스타트업의 성공을 돕다"
}
```

---

## 📝 application.yml 설정

```yaml
fastapi:
  url: http://localhost:8000

spring:
  datasource:
    url: jdbc:mysql://localhost:3306/brand_consulting
    username: root
    password: password
```

---

## 🔄 전체 흐름

```
[프론트엔드]
    ↓ (사용자 답변)
[Spring Controller]
    ↓
[Spring Service]
    ↓ (HTTP POST)
[FastAPI /step1]
    ↓ (OpenAI 분석)
[응답]
    ↓
[Spring Service]
    ├─→ user_result → DB 저장
    └─→ rag_context → Redis 저장
```

---

## ✅ 체크리스트

- [ ] FastAPI 서버 실행 (`uvicorn app.main:app --reload`)
- [ ] Spring 서버 실행
- [ ] RestTemplate Bean 설정
- [ ] DTO 클래스 생성
- [ ] Service 로직 구현
- [ ] Controller 엔드포인트 생성
- [ ] Postman으로 테스트
