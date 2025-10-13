import time
from fastapi import FastAPI, HTTPException
from utils.logger import get_logger
from models.translate_model import TranslateModel
from schemas.translate import TranslateRequest, TranslateResponse

app = FastAPI(title="AI 번역 API 서비스", version="1.0.0")
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