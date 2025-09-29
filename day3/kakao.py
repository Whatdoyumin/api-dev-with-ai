import requests, os
from dotenv import load_dotenv

BASE = "https://dapi.kakao.com/v2/search/web"

load_dotenv()
key = os.getenv("KAKAO_REST_API_KEY")
query = input("검색어 입력: ")

param = {
    "query": query,
    "size": 5
}

header = {
    "Authorization": f'KakaoAK {key}'
}

response = requests.get(url=BASE, params=param, headers=header)
print(f'요청 url: {response.url}')

if response.status_code == 200:
    data = response.json()
    documents = data.get('documents', [])
    for doc in documents:
        print(f'제목: {doc.get("title", "")}')
        print(f'요약: {doc.get("contents", "")}')
        print(f'링크: {doc.get("url", "")}\n')
else:
    print(response.status_code)