import time

START_TIME = time.time()

from fastapi import FastAPI, HTTPException
from utils.logger import get_logger
from models.translate_model import TranslateModel
from schemas.translate import TranslateRequest, TranslateResponse

from adapters.registry import registry
from schemas.infer import InferRequest, InferResponse

from services.infer_service import InferService

app = FastAPI(title="AI 텍스트 API 서비스", version="2.0.0")
logger = get_logger("translate")

translator = TranslateModel()

# infer 서비스 객체 생성
infer_service = InferService(registry, max_cocurrency=6)

# 캐시 및 상태 모니터링 엔드포인트
@app.get("/health", summary="헬스 체크")
def health_check():
    return {
        "status": "OK",
        "uptime_s": round(time.time() - START_TIME, 2)
    }

@app.get("/metrics", summary="메트릭 정보")
def metrics():
    cache_store = infer_service.cache._store
    cache_items = len(cache_store)
    uptime = round(time.time() - START_TIME, 2)
    
    sample_keys = list(cache_store.keys())[:3]
    sample_preview = [str(k) for k in sample_keys]
    
    return {
        "status": "running",
        "uptime_s": uptime,
        "cache_items": cache_items,
        "cache_sample_keys": sample_preview,
        "max_concurrency": infer_service.schema._value
    }
    
@app.delete("/clear_cache", summary="캐시 초기화")
def clear_cache():
    """인메모리 캐시 초기화"""
    infer_service.cache._store.clear()
    cleared = len(infer_service.cache._store)
    infer_service.cache._store.clear()
    return {
        "status": "cleared",
        "cache_items": cleared
    }

# 추론 엔드포인트
@app.post("/translate", response_model=TranslateResponse, summary="한영 번역")
def translate(req: TranslateRequest):
    text = req.text.strip()
    if not text:
        raise HTTPException(400, detail="텍스트가 비어있을 수 없습니다.")

    start = time.perf_counter()

    try:
        result = translator.translate(text=text, max_length=req.max_length or 256)
    except ValueError as ve:
        logger.exception(f"형식 에러: {ve}")
        raise HTTPException(400, detail=ve)
    except Exception as e:
        logger.exception(f"문제 발생: {e}")
        raise HTTPException(500, detail="번역 실패")

    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
    logger.info(f'/translate 성공 len={len(text)} ms={elapsed_ms}')
    return TranslateResponse(input_text=text, translate_text=result, elapsed_ms=elapsed_ms)

@app.get("/v1/models", summary="사용 가능한 모델 목록 조회")
def list_model():
    return {
        "models": registry.list_model()
    }
    
@app.post("/v1/infer", response_model=InferResponse, summary="텍스트 생성/분류 등 추론")
async def infer(req: InferRequest):
    if any((not t) or (not t.strip()) for t in req.inputs):
        raise HTTPException(400, detail="입력 텍스트는 비어있을 수 없습니다.")
    
    try:
        outputs = await infer_service.infer(model=req.model, texts=req.inputs, params=req.params or {})
        return {
            "model": req.model,
            "output": outputs
        }
        
    except KeyError:
        raise HTTPException(404, detail=f"모델 없음: {req.model}")
    
    except Exception as e:
        raise HTTPException(500, detail=f"추론 실패: {e}")
    

        
from fastapi import Body

@app.post("/v1/infer_detail")
async def infer_detail(
    model: str = Body(..., embed=True),
    inputs: list[str] = Body(..., embed=True),
    params: dict | None = Body(None, embed=True)
):
    
    if any((not t) or (not t.strip()) for t in inputs):
        raise HTTPException(400, detail="입력 텍스트 오류 발생")
    
    try:
        result = await infer_service.infer_with_detail(model, inputs, params)
        return result
    except KeyError:
        raise HTTPException(404, detail=f'모델 없음: {model}')
    except Exception as e:
        raise HTTPException(500, detail=f'추론 실패: {e}')