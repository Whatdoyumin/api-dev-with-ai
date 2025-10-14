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

# 멀티 프로세싱과 비교
# from multiprocessing import Pool
# -> CPU 코어 수 만큼 프로세스 생성
# -> 각 프로세스는 독립된 메모리 공간을 가짐
# -> 프로세스 간 통신이 어려움
# 대량 데이터 처리, 이미지/영상 변환, 복잡한 수학 계산 등 CPU 연산이 많이 필요한 작업에 적합