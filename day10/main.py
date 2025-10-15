import time

from fastapi.responses import StreamingResponse

START_TIME = time.time()

from fastapi import FastAPI, HTTPException
from utils.logger import get_logger
from models.translate_model import TranslateModel
from schemas.translate import TranslateRequest, TranslateResponse

from adapters.registry import registry
from schemas.infer import InferRequest, InferResponse

from services.infer_service import InferService

# 업로드 파일을 위한 라이브러리
import io, csv, json
from fastapi import UploadFile, File, Form

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
    
# 파일 업로드
async def _inputs_from_upload(file: UploadFile) -> tuple[list[str], str]:
    raw = await file.read()
    if not raw:
        raise HTTPException(400, detail="업로드 파일이 비어있음")

    text = raw.decode("utf-8", errors="replaece")
    name = (file.filename or "").lower()            # 확장자 소문자

    if name.endswith(".csv"):
        reader = csv.reader(io.StringIO(text))
        inputs = [r[0].strip() for r in reader
                  if r and isinstance(r[0], str) and r[0].strip()]
        return inputs, "csv"
    elif name.endswith(".json"):
        data = json.loads(text)
        if isinstance(data, dict) and "inputs" in data:
            arr = data["inputs"]
        elif isinstance(data, list):
            arr = data
        else:
            raise HTTPException(400, detail="지원하지 않는 JSON 형식")
        inputs = [t.strip() for t in arr
                  if isinstance(t, str) and t.strip()]
        return inputs, "json"
    else:
        raise HTTPException(400, "지원하지 않는 파일 형식")
    
@app.post("/v1/upload_infer", summary="파일 업로드로 추론")
async def upload_infer(
    model: str = Form(...),
    file: UploadFile = File(...),
    params: str | None = Form(None)
):
    inputs, ftype = await _inputs_from_upload(file)
    if not inputs:
        raise HTTPException(400, detail="유효한 데이터가 없습니다.")
    params_obj = json.loads(params) if params else None

    try:
        detail = await infer_service.infer_with_detail(model, inputs, params_obj)
    except KeyError:
        raise HTTPException(404, detail=f'모델 없음: {model}')
    
    return {
        "filename": file.filename,
        "file_type": ftype,
        "model": detail["model"],
        "count": detail["count"],
        "success": detail["success"],
        "fail": detail["fail"],
        "outputs": detail["output"],
        "errors": detail["errors"]
    }


@app.post("/v1/upload_infer_csv")
async def upload_infer_csv(
    model: str = Form(...),
    file: UploadFile = File(...),
    params: str | None = Form(None)
):
    
    inputs, _ = await _inputs_from_upload(file)
    if not inputs:
        raise HTTPException(400, detail="유효 텍스트 없음")
    
    try:
        params_obj = json.loads(params) if params else None
    except:
        raise HTTPException(400, detail="parmas가 유효한 json 형식이 아닙니다.")

    try:
        detail = await infer_service.infer_with_detail(model=model, texts=inputs, params=params_obj)
    except KeyError:
        raise HTTPException(404, detail=f'모델 없음: {model}')
    
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["index", "input", "output", "error"])

    out = detail["output"]
    errors = {
        e["index"]: e for e in detail["error"]
    } if detail.get("error") else {}

    for i, input in enumerate(inputs):
        err = errors.get(i)
        w.writerow([
            i,
            input,
            out[i] if out[i] else "",
            err if err else ""
        ])
    buf.seek(0)
    filename = (file.filename or "result").rsplit(".", 1)[0] + "_result.csv"
    header = {
        "Content-Disposition": f'attachment; filename="{filename}"'
    }
    return StreamingResponse(buf, media_type="text/csv; charset=utf-8", headers=header)