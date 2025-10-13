import time
from fastapi import FastAPI, HTTPException
from utils.logger import get_logger
from models.translate_model import TranslateModel
from schemas.translate import TranslateRequest, TranslateResponse

from adapters.registry import registry
from schemas.infer import InferRequest, InferResponse

app = FastAPI(title="AI 텍스트 API 서비스", version="2.0.0")
logger = get_logger("translate")

translator = TranslateModel()

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
def infer(req: InferRequest):
    try:
        adapter = registry.get(req.model)
    except:
        raise HTTPException(404, detail=f"모델을 찾을 수 없습니다: {req.model}")
    
    if any((not t) or (not t.strip()) for t in req.inputs):
        raise HTTPException(400, detail="입력 텍스트는 비어있을 수 없습니다.")
    
    try:
        outputs = adapter.predict(inputs=req.inputs, params=req.params or {})
    except Exception as e:
        import traceback
        print("----- 추론 중 오류 발생 -----")
        traceback.print_exc()
        print("---------------------------")

        raise HTTPException(
            500,
            detail=f"추론 중 오류: {type(e).__name__} - {e}"
        )
    
    return {
        "model": req.model,
        "output": outputs
    }
        