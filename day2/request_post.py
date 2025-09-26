import requests
import json

def pretty(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2)

BASE = "https://jsonplaceholder.typicode.com"

try:
    for user in range(1, 11):
        print(f'userId가 {user}인 사용자의 게시글') 
        response = requests.get(url=f"{BASE}/posts?userId={user}", timeout=5)
        data = response.json()
        print(pretty(data))
except:
    pass
