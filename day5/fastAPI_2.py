from fastapi import FastAPI
from pydantic import BaseModel, Field   # BaseModel은 ,Field는 조건 상세 정의

app = FastAPI(title= "POST")

class UserInput(BaseModel):
    name: str = Field(min_length=1, description="사용자 이름 (1자 이상)")
    age: int = Field(gt=0, description="나이 (양수만 허용)")

# 입력 모델: JSON 본문 구조와 검증 규칙 정의
class HelloOut(BaseModel):
    greeting: str
    length_of_name: int

@app.post("/hello", response_model=HelloOut)
def hello(user : UserInput):
    data = {
        "greeting": f"{user.name}님 나이는 {user.age}세군요!",
        "length_of_name": len(user.name)
        # response_model 덕분에 다른 키가 있어도 응답에서 제거됨
    }

    return data

# 연습문제
## 1
class AgeOut(BaseModel):
    greeting: str
    category: str

@app.post("/age-check", response_model=AgeOut)
def age_check(user: UserInput):
    age_check = "미정"
    if user.age < 20:
        age_check = "미성년자"
    else:
        age_check = "성인"

    data = {
        "greeting": f"{user.name}님 나이는 {user.age}세군요!",
        "category": f"당신은 {age_check}입니다."
    }

    return data

## 2
from typing import Optional

class FeedbackInput(BaseModel):
    message: Optional[str] = Field(min_length=1, default="리뷰 없음")   # Optional로 입력 필수 X
    rating: int = Field(ge=1, le=5)

@app.post("/feedback")
def feedback(feedback: FeedbackInput):
    return {"rating": feedback.rating, "message": feedback.message}