import requests, os
from dotenv import load_dotenv
from datetime import datetime
import json

load_dotenv()

key = os.getenv("KAKAO_REST_API_KEY")
token = os.getenv("KAKAO_ACCESS_TOKEN")

def search_kakao(query):
    url = "https://dapi.kakao.com/v2/search/web"
    headers = {"Authorization": f"kakaoAK {key}"}
    params = {
        "query": query,
        "sort": "accuracy",
        "size": 3,
        "page": 1
    }

    resp = requests.get(url=url, headers=headers, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json().get("documents", [])

def build_message(qauery, docs):
    lines = [f'웹 검색 결과 | 키워드: {qauery}\n']
    if not docs:
        lines.append("검색 결과 없음")
    else:
        for doc in docs:
            title = doc.get("title", "")
            url = doc.get("url", "")
            ts = doc.get("datetime")
            date_str = ""

            if ts :
                try:
                    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    date_str = f" ({dt.strftime('%Y-%m-%d')})"
                except Exception:
                    pass
            lines.append(f"{i}, {title}{date_str}\n    {url}")

    msg = "\n".join(lines)
    return msg

def send_kakao_message(text):
    BASE = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {
        "Authorization": f'Bearer {token}',
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
    }
    template = {
        "object_type": "text",
        "text": text,
        "link": {
            "web_url": "http://www.daum.net",
            "mobile_web_url": "http://m.daum.net",
        },
        "button_title": "열기"
    }

    data = {
        "template_object": json.dumps(template, ensure_ascii=False)
    }
    response = requests.post(url=BASE, headers=headers, data=data)
    
    if response.status_code == 200:
        print("전송 성공")
        print(response.json().get("result_code", -1))
    else:
        print("전송 실패")

if __name__ == "__main__":
    query = input("검색 키워드 입력: ")
    docs = search_kakao(query)
    msg = build_message(query, docs)
    print(msg)
    send_kakao_message(msg)