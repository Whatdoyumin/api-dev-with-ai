import asyncio
import time
from fastapi import FastAPI

app = FastAPI()

def slow_task_sync():
    time.sleep(2)
    return "동기 함수 완료"

async def slow_task_async():
    await asyncio.sleep(2)
    return "비동기 함수 완료"

@app.get("/test_sync")
def test_sync():
    start = time.perf_counter()     # 시작 시간 기록
    for _ in range(3):
        slow_task_sync()  # 동기 함수 호출
    return {
        "duration": round(time.perf_counter() - start, 2)
    } 
# 동기 함수 실행 결과: 
# {"duration": 6.01}
    
@app.get("/test_async")
async def test_async():
    start = time.perf_counter()
    tasks = [slow_task_async() for _ in range(3)]   # 비동기 함수 호출
    await asyncio.gather(*tasks)  # 모든 비동기 함수가 완료될 때까지 대기
    return {
        "duration": round(time.perf_counter() - start, 2)
    } 
# 비동기 함수 실행 결과: 
# {"duration": 2}