import requests
import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("WEATHERAPI_KEY")

CITY = "Seo"
TIMEOUT = 5

BASE = "http://api.weatherapi.com/v1/current.json"

param = {
    "key": key,
    "q": CITY,
    "aqi": "no"
}

try:
    response = requests.get(url=BASE, params=param, timeout=TIMEOUT)
    response.raise_for_status()

    data = response.json()
    print("OK")
    print(data.get("location", {}).get("name", ""))
    print(data.get("current", {}).get("temp_c", ""))

except requests.exceptions.HTTPError as e:
    code = response.json().get("error", {}).get("code", -1)
    if code == 1003:
        print("1003번 오류")
    
    elif code == 1006:
        print("1006번 오류")
    
    else:
        msg = ''
        try:
            msg = response.json().get("error", {}).get("message", "")
        except:
            msg = response.text
        print(f'HTTP 오류 {response.status_code}')