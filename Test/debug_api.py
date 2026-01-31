import requests
import json

# sample_answers.json 읽기
with open("sample_answers.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("=" * 60)
print("📤 요청 데이터:")
print(json.dumps(data, indent=2, ensure_ascii=False))
print("=" * 60)

# API 호출
url = "http://localhost:8000/api/v1/diagnosis/step1"
headers = {"Content-Type": "application/json"}

try:
    response = requests.post(url, json=data, headers=headers)
    
    print(f"\n📊 응답 상태 코드: {response.status_code}")
    print("=" * 60)
    
    if response.status_code == 200:
        print("✅ 성공!")
        result = response.json()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("❌ 에러 발생!")
        print(response.text)
        
except Exception as e:
    print(f"❌ 요청 실패: {str(e)}")
