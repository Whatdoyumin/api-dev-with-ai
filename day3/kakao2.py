import requests, os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("KAKAO_REST_API_KEY")
query = input("상호명 입력: ")

BASE = "https://dapi.kakao.com/v2/local/search/keyword.json"

param = {
    "query": query,
    "size": 5
}

header = {
    "Authorization": f'KakaoAK {key}'
}

response = requests.get(url=BASE, params=param, headers=header)

if response.status_code == 200 :
    data = response.json()
    for doc in data.get("documents", []):
        #상호명, 도로명주소, 전화번호, 지도링크
        print(f"\n상호명: {doc.get('place_name', '')}")
        print(f"도로명주소: {doc.get('road_address_name', '')}")
        print(f"전화번호: {doc.get('phone', '')}")
        print(f"지도 링크: {doc.get('place_url', '')}")

else:
    print(response.status_code)