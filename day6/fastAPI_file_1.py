from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field
from uuid import uuid4
from typing import Dict, Optional, List

app = FastAPI(title="CRUD")

class Memo(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1, max_length=1000)

class MemoOut(BaseModel):
    id: str
    title: str
    content: str

MEMOS: Dict[str, Memo] = {}

@app.post("/memo", response_model=MemoOut, status_code=status.HTTP_201_CREATED)
def create_memo(memo: Memo):
    mid = uuid4().hex
    MEMOS[mid] = memo
    return {"id": mid, **memo.model_dump()}

@app.get("/memo/{mid}", response_model=MemoOut)
def read_memo(mid: str):
    if mid not in MEMOS:
        raise HTTPException(status_code=404, detail="Memo not found")
    return {"id": mid, **MEMOS[mid].model_dump()}

@app.get("/memos")
def read_memos(
    q: Optional[str] = Query(default=None, description="제목 부분검색 키워드"),
    limit: int = Query(default=10, ge=1, le=100, description="최대 개수"),
    offset: int = Query(default=0, ge=0, description="건너뛸 데이터 개수")
):
    
    # title과 content만 있는 딕셔너리 -> id, title, content가 있는 리스트로 변환
    items: List[Dict] = [{"id": mid, **m.model_dump()} for mid, m in MEMOS.items()]

    if q:
        # 검색어가 있다면, 검색어를 소문자로 변환합니다.
        q_lower = q.lower()
        # items의 각 데이터에 대해서, title이 검색어를 포함하고 있다면 items에 넣고, 그렇지 않다면 무시하고 넘어갑니다.
        items = [it for it in items if q_lower in it["title"].lower()]

    total = len(items)
    # offest번째 데이터부터 검색해서, 최대 limit 개의 데이터를 표시하기 위함
    page = items[offset : offset + limit]

    return {"total": total, "limit": limit, "offset": offset, "items": page}

