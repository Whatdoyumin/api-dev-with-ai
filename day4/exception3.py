import requests
import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("WEATHERAPI_KEY")

CITY = ["Seoul", "London", "NewYork", "Tokyo", "",
"Seoullll"]
TIMEOUT = 3
MAX_RETRY = 2

BASE = "http://api.weatherapi.com/v1/current.json"

# for city in CITY:
#     param = {
#     "key": key,
#     "q": city,
#     "aqi": "no"
#     }
    
#     response = requests.get(url=BASE, params=param, timeout=TIMEOUT)
#     response.raise_for_status()

#     data = response.json()
#     print("OK")
#     print(data.get("location", {}).get("name", ""))
#     print(data.get("current", {}).get("temp_c", ""))
    
#     if response.status_code == 401 | response.status_code == 404 | response.status_code == 403 | response.status_code == 404:
#         for i in 2:
#             response = requests.get(url=BASE, params=param, timeout=TIMEOUT)
#             response.raise_for_status()

#             data = response.json()
#             print("RETRY")
#             print(data.get("location", {}).get("name", ""))
#             print(data.get("current", {}).get("temp_c", ""))
#     elif response.status_code == 500:
#         break
#     else:
#         print(response.status_code)


## 강사님 답변
for city in CITY:
    param = {
        "key": key,
        "q": city,
        "aqi": "no"
    }
    attempt = 0

    while True:
        try:
            response = requests.get(url=BASE, params=param, timeout=TIMEOUT)
            response.raise_for_status()

            data = response.json()

            name = data.get("location", {}).get("name", "")
            temp = data.get("current", {}).get("temp_c", "")

            print(f'OK  | {name} | {temp} ℃')
            break

        except requests.exceptions.HTTPError as e:
            try:
                data = response.json()
                err = data.get("error", {})
                code = err.get("code", "")
                msg = err.get("message", "")
            except:
                msg = err.text
            
            if 400 <= response.status_code < 500 and attempt < MAX_RETRY:
                attempt += 1
                print(f'RETRY   | {city} | 4xx {response.status_code} | {code} {msg} -> {attempt}/{MAX_RETRY}')
                continue
            
            print(f'FAIL    | {city} | {msg or e}')
            break

        except requests.exceptions.Timeout as e:
            if attempt < MAX_RETRY:
                attempt += 1
                print(f'RETRY   | {city} | timeout')
                continue
            
            print(f'FAIL    | {city} timeout | {e}')
            break

        except requests.exceptions.ConnectionError as e:
            if attempt < MAX_RETRY:
                attempt += 1
                print(f'RETRY   | {city} | connection error')
                continue
            
            print(f'FAIL    | {city} connection error | {e}')
            break            

        except requests.exceptions.RequestException as e:
            if attempt < MAX_RETRY:
                attempt += 1
                print(f'RETRY   | {city} | request error')
                continue
            
            print(f'FAIL    | {city} request error | {e}')
            break