import os, sys, json
import requests
from dotenv import load_dotenv

def pretty(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2)

BASE = "http://api.weatherapi.com/v1"

load_dotenv()
key = os.getenv("WEATHERAPI_KEY")
url = f"{BASE}/forecast.json"

print("[STEP4] 사용자 입력 도시 -> forecast 3일 조회 -> 파싱")

city = input("도시명을 입력하세요(예: 서울) : ")

try:
    params = {"key": key, "q": city, "days": 3, "aqi": "no", "alerts": "no"}
    response = requests.get(url=url, params=params, timeout=2)
    print("요청 URL:", response.url)
    print("status:", response.status_code)
    response.raise_for_status()
    data = response.json()

    location = data.get("location", {})
    cur = data.get("current", {})
    
    for day in data.get("forecast", {}).get("forecastday", []):
        date = day.get("date")
        day_info = day.get("day", {})
        print(f"날짜: {date}")
        print(f"  최고온도(°C): {day_info.get('maxtemp_c')} / 최저온도(°C): {day_info.get('mintemp_c')}")
        print(f"  최저온도(°C): {day_info.get('mintemp_c')}")
        print(f"  날씨: {(day_info.get('condition') or {}).get('text')}")

except requests.HTTPError as e:
    print("HTTPError:", e)
    try:
        print(pretty(response.json()))
    except Exception:
        pass
except Exception as e:
    print("요청 실패:", e)