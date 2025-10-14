import time
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
    
        