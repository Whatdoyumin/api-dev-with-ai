import os, sys, json
import requests

def pretty(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2)

BASE = "http://api.weatherapi.com/v1"

print("[STEP] 키 포함하여 날씨 조회")

key = os.environ.get("WEATHERAPI_KEY")
if not key:
    print("환경변수 WEATHERAPI_KEY가 설정되어 있지 않습니다.")
    print("Mac/Linux 예) export WEATHERAPI_KEY=\"발급받은키\"")
    print("Windows PowerShell 예) $Env:WEATHERAPI_KEY=\"발급받은키\"")
    sys.exit(1)

url = f"{BASE}/forecast.json"


cities = ["Seoul", "Paris", "London"]


try:

    for city in cities:
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
            print(f"  평균온도(°C): {day_info.get('avgtemp_c')}")
            print(f"  날씨: {(day_info.get('condition') or {}).get('text')}")

except requests.HTTPError as e:
    print("HTTPError:", e)
    try:
        print(pretty(response.json()))
    except Exception:
        pass
except Exception as e:
    print("요청 실패:", e)