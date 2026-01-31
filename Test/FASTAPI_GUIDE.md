# FastAPI Step 1 Diagnosis 서버 사용 가이드

## 📁 프로젝트 구조

```
Test/
├── app/
│   ├── __init__.py
│   ├── main.py                        # FastAPI 메인 애플리케이션
│   ├── models.py                      # Pydantic 모델 정의
│   └── services/
│       ├── __init__.py
│       └── diagnosis_service.py       # 진단 분석 로직
├── test.json                          # 질문 데이터
├── sample_answers.json                # 테스트용 답변
├── requirements.txt                   # 패키지 의존성
├── .env                               # 환경변수 (API 키)
└── test_diagnosis.py                  # 기존 실험 스크립트
```

## 🚀 시작하기

### 1. 패키지 설치

```bash
cd "c:\Users\User\Desktop\개발 파일\Test"
pip install -r requirements.txt
```

### 2. 서버 실행

```bash
# 개발 모드 (auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 또는 간단하게
uvicorn app.main:app --reload
```

서버가 실행되면:
- 🌐 API: `http://localhost:8000`
- 📚 Swagger UI: `http://localhost:8000/docs`
- 📖 ReDoc: `http://localhost:8000/redoc`

## 📡 API 엔드포인트

### 1. 루트 엔드포인트
```bash
GET http://localhost:8000/
```

**응답**:
```json
{
    "message": "Brand Consulting AI API",
    "status": "running",
    "version": "1.0.0"
}
```

### 2. 헬스 체크
```bash
GET http://localhost:8000/health
```

**응답**:
```json
{
    "status": "healthy"
}
```

### 3. Step 1 진단 분석 (메인)
```bash
POST http://localhost:8000/api/v1/diagnosis/step1
Content-Type: application/json
```

**요청 본문** (`sample_answers.json` 형식):
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

**응답**:
```json
{
    "user_result": {
        "summary": "비즈니스 한 줄 요약",
        "keywords": ["키워드1", "키워드2", ...],
        "analysis": "통합 분석 (300자 이내)",
        "key_insights": "핵심 인사이트"
    },
    "rag_context": {
        "step_1_analysis": {
            "summary": "...",
            "keywords": [...],
            "analysis": "...",
            "key_insights": "..."
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
}
```

### 4. 테스트 엔드포인트
```bash
POST http://localhost:8000/api/v1/diagnosis/step1/test
```

`sample_answers.json` 파일을 자동으로 읽어서 분석합니다.

## 🧪 테스트 방법

### 방법 1: Swagger UI 사용 (추천)
1. 브라우저에서 `http://localhost:8000/docs` 접속
2. `POST /api/v1/diagnosis/step1/test` 클릭
3. "Try it out" 버튼 클릭
4. "Execute" 버튼 클릭
5. 응답 확인

### 방법 2: curl 사용
```bash
# 테스트 엔드포인트
curl -X POST "http://localhost:8000/api/v1/diagnosis/step1/test"

# 직접 데이터 전송
curl -X POST "http://localhost:8000/api/v1/diagnosis/step1" \
  -H "Content-Type: application/json" \
  -d @sample_answers.json
```

### 방법 3: Python requests
```python
import requests
import json

# 테스트 엔드포인트
response = requests.post("http://localhost:8000/api/v1/diagnosis/step1/test")
print(response.json())

# 직접 데이터 전송
with open("sample_answers.json", "r", encoding="utf-8") as f:
    data = json.load(f)

response = requests.post(
    "http://localhost:8000/api/v1/diagnosis/step1",
    json=data
)
print(response.json())
```

## 🔗 Spring 백엔드 연동

### Spring RestTemplate 예시

```java
@Service
public class DiagnosisService {
    
    private final RestTemplate restTemplate;
    private final String fastApiUrl = "http://localhost:8000/api/v1/diagnosis/step1";
    
    public DiagnosisResponse analyzeDiagnosis(DiagnosisRequest request) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        
        HttpEntity<DiagnosisRequest> entity = new HttpEntity<>(request, headers);
        
        ResponseEntity<DiagnosisResponse> response = restTemplate.postForEntity(
            fastApiUrl,
            entity,
            DiagnosisResponse.class
        );
        
        return response.getBody();
    }
}
```

### Spring WebClient 예시 (비동기)

```java
@Service
public class DiagnosisService {
    
    private final WebClient webClient;
    
    public DiagnosisService(WebClient.Builder webClientBuilder) {
        this.webClient = webClientBuilder
            .baseUrl("http://localhost:8000")
            .build();
    }
    
    public Mono<DiagnosisResponse> analyzeDiagnosis(DiagnosisRequest request) {
        return webClient.post()
            .uri("/api/v1/diagnosis/step1")
            .contentType(MediaType.APPLICATION_JSON)
            .bodyValue(request)
            .retrieve()
            .bodyToMono(DiagnosisResponse.class);
    }
}
```

## ⚙️ 환경변수 설정

`.env` 파일에서 설정 가능:

```env
OPENAI_API_KEY=your-api-key-here
PORT=8000
```

## 🔧 문제 해결

### 1. 포트가 이미 사용 중인 경우
```bash
# 다른 포트로 실행
uvicorn app.main:app --reload --port 8001
```

### 2. OpenAI API 키 오류
- `.env` 파일에 올바른 API 키가 설정되어 있는지 확인
- 환경변수가 제대로 로드되는지 확인

### 3. CORS 오류
`app/main.py`에서 CORS 설정 확인:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Spring 서버 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📊 응답 데이터 활용

### user_result (DB 저장용)
- Spring에서 받아서 데이터베이스에 저장
- 사용자에게 UI로 표시

### rag_context (누적 컨텍스트용)
- Step 2, 3, 4... 에서 참조할 데이터
- 파일 또는 Redis에 저장 권장
- 다음 단계 API 호출 시 함께 전송

## 🚀 다음 단계

1. **Step 2 네이밍 API 추가**
2. **Step 3-8 API 순차 구현**
3. **RAG 컨텍스트 저장소 연동** (Redis/DB)
4. **인증/인가 추가** (JWT)
5. **로깅 및 모니터링**
6. **Docker 컨테이너화**

## 📝 참고사항

- OpenAI API 호출 시 비용이 발생합니다
- 응답 시간은 보통 3-5초 정도 소요됩니다
- 프로덕션 배포 시 CORS 설정을 특정 도메인만 허용하도록 변경하세요
