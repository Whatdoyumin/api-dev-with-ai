import os, json
import requests
from dotenv import load_dotenv

def pretty(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2)

BASE = "http://api.weatherapi.com/v1"

load_dotenv()
key = os.getenv("WEATHERAPI_KEY")

city = "Seoul"
url = f'{BASE}/forecast.json'
p = {"key": key, "q": city, "days": 1, "aqi": "no", "alerts": "no"}

response = requests.get(url=url, params=p, timeout=3)
data = response.json()

l = data.get("location", {})
c = data.get("current", {})
f = data.get("forecast", {})

cond = c.get("condition", {})
cond_text = c.get("cond", "")

print(cond_text)

forecastday = f.get("forecastday", [])[0]
hours = forecastday.get("hour", [])

for hour in hours:
    time = hour.get("time", "")
    feelslike_c = hour.get("feelslike_c", "")
    hour_cond = hour.get("condition", {})
    hour_cond_text = hour_cond.get("text", "")


    print(f'시간: {time}')
    print(f"체감온도: {feelslike_c}")
    print(f"날씨: {hour_cond_text}")
