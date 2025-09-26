import requests
import json

def pretty(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2)

BASE = "http://api.weatherapi.com/v1"

url = f"{BASE}/current.json"

try:
    response = requests.get(url=url, timeout=2)

    print("요청 URL: ", response.url)
    print("statue: ", response.status_code)

    # 성공/실패와 무관하게 본문을 출력 (에러 json 구조 확인 목적)
    print("응답 본문: ", pretty(response.json()))

except Exception as e:
    print("요청 실패: ", e)