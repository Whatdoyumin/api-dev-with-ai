import time

START_TIME = time.time()

from fastapi import FastAPI, HTTPException
from utils.logger import get_logger
from models.translate_model import TranslateModel
from schemas.translate import TranslateRequest, TranslateResponse

from adapters.registry import registry
from schemas.infer import InferRequest, InferResponse

from services.infer_service import InferService

import io, csv, json
from fastapi import UploadFile, File, Form
from fastapi.responses import StreamingResponse

import math, asyncio
from typing import Any
from fastapi import Depends, Security

import os
from fastapi.security import APIKeyHeader, APIKeyQuery

API_KEY_NAME = "X-API-Key"
API_KEYS = set((os.getenv("API_KEYS") or "ai-training-secret-2025").split(","))
print(API_KEYS)
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
api_key_query = APIKeyQuery(name="api_key", auto_error=False)

async def require_api_key(
    key_h: str | None = Security(api_key_header),
    key_q: str | None = Security(api_key_query)
):
    key = key_h or key_q
    if not key or key not in API_KEYS:
        raise HTTPException(403, detail="잘못된 키")
    return key

def _cos(a: list[float], b: list[float]) -> float:
    s = sum(x*y for x, y in zip(a, b))
    na = math.sqrt(sum(x*x for x in a)) or 1e-12
    nb = math.sqrt(sum(x*x for x in b)) or 1e-12
    return s / (na * nb)

_VEC_DB: dict[str, list[dict[str, Any]]] = {}

app = FastAPI(title="AI 텍스트 API 서비스", version="2.1.0")

logger = get_logger("translate")
translator = TranslateModel()

infer_service = InferService(registry)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "uptime_s": round(time.time() - START_TIME, 2)
    }

@app.get("/metrics")
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
        "max_concurrency": infer_service.sema._value
    }

@app.delete("/clear_cache")
def clear_cache():
    cleared = len(infer_service.cache._store)
    infer_service.cache._store.clear()
    return {
        "status": "cleared",
        "cleared_items": cleared
    }

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

@app.get("/v1/models")
def list_models(_apikey: str = Security(require_api_key)):
    return {
        "models": registry.list_model()
    }

@app.post("/v1/infer", response_model=InferResponse)
async def infer(req: InferRequest):
    if any((not t) or (not t.strip()) for t in req.inputs):
        raise HTTPException(400, detail="입력 텍스트 오류 발생")

    try:
        outputs = await infer_service.infer(req.model, req.inputs, req.params)
        return {
            "model": req.model,
            "output": outputs
        }
    except KeyError:
        raise HTTPException(404, detail=f'모델 없음: {req.model}')

    except Exception as e:
        raise HTTPException(500, detail=f'추론 실패: {e}')
    
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
    
async def _inputs_from_upload(file: UploadFile) -> tuple[list[str], str]:
    raw = await file.read()
    if not raw:
        raise HTTPException(400, detail="빈 파일")
    
    text = raw.decode("utf-8", errors="replace")
    name = (file.filename or "").lower()

    if name.endswith(".csv"):
        reader = csv.reader(io.StringIO(text))
        inputs = [r[0].strip() for r in reader
                  if r and isinstance(r[0], str) and r[0].strip()]
        return inputs, "csv"
    
    elif name.endswith(".json"):
        data = json.loads(text)
        if isinstance(data, dict) and "inputs" in data:
            array = data["inputs"]
        elif isinstance(data, list):
            array = data
        else:
            raise HTTPException(400, detail="지원하지 않는 json 구조")
        inputs = [t.strip() for t in array
                  if isinstance(t, str) and t.strip()]
        return inputs, "json"
    
    else:
        raise HTTPException(400, "지원하지 않는 형식")
    
@app.post("/v1/upload_infer")
async def upload_infer(
    model: str = Form(...),
    file: UploadFile = File(...),
    params: str | None = Form(None)
):
    inputs, ftype = await _inputs_from_upload(file)
    if not inputs:
        raise HTTPException(400, detail="유효한 데이터 없음")
    parmas_obj = json.loads(params) if params else None

    try:
        detail = await infer_service.infer_with_detail(model=model, texts=inputs, params=parmas_obj)
    except KeyError:
        raise HTTPException(404, detail=f'모델 없음: {model}')
    
    return {
        "filename": file.filename,
        "filetype": ftype,
        "model": detail["model"],
        "count": detail["count"],
        "success": detail["success"],
        "fail": detail["fail"],
        "output": detail["output"],
        "errors": detail["error"]
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

@app.post("/v1/embeddings")
async def embeddings(
    model: str = Body(..., embed=True),
    inputs: list[str] = Body(..., embed=True),
    params: dict | None = Body(None, embed=True)
):
    try:
        adapter = registry.get(model)
    except:
        raise HTTPException(404, detail=f'잘못된 모델: {model}')
    
    vectors = await asyncio.to_thread(adapter.embed, inputs)

    return {
        "model": model,
        "count": len(vectors),
        "vectors_preview": vectors[:2]
    }

@app.post("/v1/vec/upsert")
async def vec_upsert(
    model: str = Body(..., embed=True),
    namespace: str = Body("default", embed=True),
    items: list[dict] = Body(..., embed=True),
    params: dict | None = Body(None, embed=True)
):
    if not items:
        raise HTTPException(400, detail="items 비어 있음.")

    valid_items: list[tuple[dict, str]] = []

    for item in items:
        text = item.get("text")
        if isinstance(text, str):
            s = text.strip()
            if s:
                valid_items.append((item, s))

    if not valid_items:
        raise HTTPException(400, detail="유효한 텍스트가 없습니다.")
    
    texts = [s for _, s in valid_items]

    try:
        adapter = registry.get(model)
    except Exception:
        raise HTTPException(404, detail=f'모델 없음: {model}')

    vecs = await asyncio.to_thread(adapter.embed, texts)

    if len(vecs) != len(texts):
        raise HTTPException(500, detail="임베딩 실패")
    
    db = _VEC_DB.setdefault(namespace, [])
    now = time.time()

    id2idx = {e["id"]: i for i, e in enumerate(db)}

    added = 0
    updated = 0

    for (it, s), v in zip(valid_items, vecs):
        eid = it.get("id")
        entry = {
            "id": eid,
            "text": s,
            "vec": v,
            "meta": it.get("metadata") or {},
            "ts": now
        }
        if eid in id2idx:
            db[id2idx[eid]] = entry
            updated += 1
        else:
            db.append(entry)
            id2idx[eid] = len(db) - 1
            added += 1

    return {
        "namespace": namespace,
        "added": added,
        "updated": updated,
        "size": len(db)
    }

@app.post("/v1/vec/query")
async def vec_query(
    model: str = Body(..., embed=True),
    namespace: str = Body("default", embed=True),
    query: str = Body(..., embed=True),
    top_k: int = Body(5, embed=True),
    params: dict | None = Body(None, embed=True)
):
    q = query.strip()
    if not q:
        raise HTTPException(400, detail="query 비어 있음")
    
    db = _VEC_DB.get(namespace, [])
    if not db:
        return {
            "namespace": namespace,
            "query": q,
            "matches": []
        }

    try:
        adapter = registry.get(model)
    except:
        raise HTTPException(404, detail=f'모델 없음: {model}')
    
    qv =  (await asyncio.to_thread(adapter.embed, [q]))[0]

    scored = [{
        "id": e["id"],
        "text": e["text"],
        "score": _cos(qv, e["vec"]),
        "metadata": e["meta"]
    } for e in db]

    scored.sort(key=lambda x: x["score"], reverse=True)

    return {
        "namespace": namespace,
        "query": q,
        "top_k": top_k,
        "matches": scored[:top_k]
    }