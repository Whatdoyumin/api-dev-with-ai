from fastapi import FastAPI, File, UploadFile
from typing import List

app = FastAPI(title="File Upload API")

# 단일 파일 업로드 테스트
@app.post("/upload_test")
async def upload_test(file: UploadFile = File(...)):
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": len(await file.read()),
        "size": file.size
    }

# 다중 파일 업로드 테스트
@app.post("/upload_multi")
async def upload_multi(files: List[UploadFile] = File(...)):
    return [
        {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": file.size
        }
        for file in files
    ]

import io, csv
from fastapi import HTTPException

# CSV 파일 파싱 및 내용 추출
@app.post("/parse_csv")
async def parse_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(400, detail="CSV 파일이 아닙니다.")
    
    raw = await file.read()
    text = raw.decode("utf-8")

    reader = csv.reader(io.StringIO(text))
    rows = [row for row in reader]          # 각 행을 리스트로 변환하여 rows에 저장

    inputs = [
        row[0].strip() for row in rows 
        if row and isinstance(row[0], str) and row[0].strip()   # 첫 번째 열이 비어있지 않고 문자열인 경우에만 추가
    ]

    return {
        "filename": file.filename,
        "total_rows": len(rows),
        "valid_inputs": len(inputs),
        "inputs": inputs[:5]
    }

import json

# JSON 파일 파싱 및 내용 추출
@app.post("/parse_json")
async def parse_json(file: UploadFile = File(...)):
    if not file.filename.endswith(".json"):
        raise HTTPException(400, detail="json이 아닙니다.")
    
    raw = await file.read()
    text = raw.decode("utf-8")

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        raise HTTPException(400, detail="json 파싱 오류")
    
    if isinstance(data, dict) and "inputs" in data:
        inputs = [t.strip() for t in (data["inputs"] if isinstance(data["inputs"], list) else data) 
                  if isinstance(t, str) and t.strip()]
    elif isinstance(data, list):
        inputs = data
        inputs = [t.strip() for t in inputs if isinstance(t, str) and t.strip()]
    else:
        raise HTTPException(400, detail="지원하지 않는 json 형식")
    
    return {
        "filename": file.filename,
        "count": len(inputs),
        "sample": inputs[:5]
    }

# 파일 확장자에 따라 CSV 또는 JSON 파싱
@app.post("/parse_file")
async def parse_file(file: UploadFile = File(...)):
    raw = await file.read()
    text = raw.decode("utf-8")\
    
    if file.filename.endswith(".csv"):
        reader = csv.reader(io.StringIO(text))
        inputs = [r[0].strip() for r in reader
                  if r and isinstance(r[0], str) and r[0].strip()]
        return {
            "count": len(inputs),
            "sample": inputs[:5]
        }
    elif file.filename.endswith(".json"):
        data = json.loads(text)
        if isinstance(data, dict) and "inputs" in data:
            array = data["inputs"]
        elif isinstance(data, list):
            array = data
        else:
            raise HTTPException(400, detail="지원하지 않는 json 형식")
    else:
        raise HTTPException(400, detail="지원하지 않는 파일 형식")
    
    inputs = [t.strip() for t in array
              if isinstance(t, str) and t.strip()]
    
    return {
        "count": len(inputs),
        "sample": inputs[:5]
    }