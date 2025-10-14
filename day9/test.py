import asyncio

async def say_hello():
    print("시작")
    
    # 2초 대기
    await asyncio.sleep(2)
    
    print("종료")
    
async def main():
    await asyncio.gather(say_hello(), say_hello(), say_hello())
    
asyncio.run(main())