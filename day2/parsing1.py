import json

def pretty(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2)

raw = """
{
    "id": 1,
    "name": "김민석",
    "skills": ["RPA", "API"],
    "profile": {
        "email": "kim@email.com",
        "phone": "010-1234-5678"
    }
}
"""

obj = json.loads(raw)

# 타입 확인
# print(type(raw))
# print(type(obj))

print(obj.get("id"))
print(obj["id"])

# 에러
# print(obj["123"])

# 안전하도록 get 사용
print(obj.get("123", {}))

# skills 접근 및 타입 확인
print(obj.get("skills", []))
print(type(obj.get("skills", [])))
# 하나씩 출력
for e in obj.get("skills", []):
    print(e)

#profile 접근 및 타입 확인
d = obj.get("profile", {})
print(d)
print(type(d))

dd = d.get("email", {})
print(dd)
print(type(dd))
print(obj["profile"]["email"])
