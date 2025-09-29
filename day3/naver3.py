import requests
import html, re
import os
from dotenv import load_dotenv

load_dotenv()

BASE = 'https://openapi.naver.com/v1/search/blog.json'
CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

def html_clean(text):
    # html 태그를 제거하는 함수
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", '', text)
    return text


query = input("검색어 입력: ")

param = {
    "query": query,
    "display": 3
}

header = {
    "X-Naver-Client-Id": CLIENT_ID,
    "X-Naver-Client-Secret": CLIENT_SECRET
}

response = requests.get(url=BASE, params=param, headers=header, timeout=5)
print(f'요청 URL: {response.url}')

if response.status_code == 200:
    data = response.json()
    items = data.get('items', [])

    for item in items:
        title = item.get('title', '')
        desc = item.get('description', '')

        print(f'포스트 제목: {title}')
        print(f'요약: {desc}\n')

else:
    print(f'상태 코드: {response.status_code}')
