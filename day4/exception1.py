import requests
import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("WEATHERAPI_KEY")

CITY = "Seoul"
TIMEOUT = 5

BASE = "http://api.weatherapi.com/v1/current.json"

param = {
    "key": key,
    "q": CITY,
    "aqi": "no"
}

try:
    response = requests.get(url=BASE, params=param, timeout=TIMEOUT)
    data = response.json()
    print(f'호출 성공: {data.get("location", {}).get("name", "")} {data.get("current", {}).get("temp_c", 0)}')

except requests.exceptions.Timeout:
    print("타임아웃 발생")
except requests.exceptions.ConnectionError:
    print("네트워크 연결 오류")
except ValueError:
    print("JSON 파싱 오류")
except requests.exceptions.RequestException as e:
    print("기타 요청 오류", e)