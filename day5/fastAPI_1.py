from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "안녕하세요"}

@app.get("/greet")
def greet(name: str = "friend"):
    return {"message": f"Hi, {name}!"}

@app.get("/square/{number}")
def square(number: int):
    return {"result": number ** 2}

# 연습문제
## 1
@app.get("/sum")
def sum(num1: int = 0, num2: int = 0):
    data = {
        "num1": num1,
        "num2": num2,
        "sum": num1 + num2
    }

    return data

## 2
@app.get("/welcome")
def welcome(lang: str = "en"):
    # word = "Hello"

    # if lang == "ko":
    #     word = "안녕하세요"
    # elif lang == "en":
    #     word = "Hello"
    
    # return {"message": word}

    greeting = {
        "ko": "안녕하세요",
        "en": "Hello"
    }

    data = {
        "lang": lang,
        "greeting": greeting.get(lang, "Hello")
    }

    return data