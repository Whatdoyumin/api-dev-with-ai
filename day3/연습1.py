import requests, os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BASE = 'https://openapi.naver.com/v1/search/blog.json'
CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

query = input("검색어 입력: ")

param = {
    "query": query,
    "display": 50,
    "sort": "sim"
}

header = {
    "X-Naver-Client-Id": CLIENT_ID,
    "X-Naver-Client-Secret": CLIENT_SECRET
}

response = requests.get(url=BASE, params=param, headers=header, timeout=5)
today = datetime.now().strftime("%Y%m%d")

if response.status_code == 200:
    data = response.json()
    items = data.get("items", [])

    for item in items:
        postdate = item.get("postdate", "")
        if postdate == today:
            print(f'작성일 : {postdate}')
            print(f'포스트제목 : {item.get("title", "")}')
            print(f'블로그이름 : {item.get("bloggername", "")}')
            print(f'링크 : {item.get("link", "")}\n')

else:
    print(response.status_code)