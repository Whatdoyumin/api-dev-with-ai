from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from uuid import uuid4
from typing import Dict, Optional, List

app = FastAPI(title="CRUD")

# 입력 모델
class Memo(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1, max_length=1000)

# 메모리 딕셔너리
MEMOS: Dict[str, Memo] = {}

@app.post("/memo")
def create_memo(memo: Memo):
    m_id = uuid4().hex
    MEMOS[m_id] = memo
    return {"id": m_id}

@app.get("/memos")
def read_memos(
    q: Optional[str] = Query(default=None, description="제목 부분 검색 키워드"),
    limit: int = Query(default=10, le=100, description="최대 개수"),
    offset: int = Query(default=0, ge=0, description="건너뛸 데이터 개수")
):
    # title과 content만 있는 딕셔너리를 -> id, title, content가 있는 리스트로 변환
    items: List[Dict] = [{"id": m_id, **m.model_dump()} for m_id, m in MEMOS.items()]
    # m.model_dump() -> 모델(m)의 데이터를 딕셔너리(dict)로 변환
    # ** -> 언패킹하여 "title": "제목1", "content": "내용1" 형태로 삽입

    if q:
        # 검색어가 있다면, 검색어를 소문자로 변환합니다.
        q_lower = q.lower()
        # items의 각 데이터에 대해서, title이 검색어를 포함하고 있다면 items에 넣고, 그렇지 않다면 무시하고 넘어갑니다.
        items = [it for it in items if q_lower in it["title"].lower()]
    
    total = len(items)
    # offset번째 데이터부터 검색해서 최대 limit 개의 데이터를 표시하기 위함
    page = items[offset: offset + limit]
    
    data = {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": page
    }
    return data

# b. 제목 완전일치 검색하여 한 건의 결과를 반환
#    제목이 완전히 같은 메모가 두 개 이상 나올 경우, 부분 검색을 이용해 달라고 안내메시지 출력
@app.get("/memo/bytitle/{title}")
def read_memo_by_title(title: str):
    matched = [(m_id, m) for m_id, m in MEMOS.items() if m.title == title]

    if not matched:
        raise HTTPException(404, detail="검색 결과가 없습니다.")
    
    if len(matched) > 1:
        raise HTTPException(409, detail="여러 건이 검색되었습니다. 부분 검색을 이용하세요.")
    
    m_id, m = matched[0]

    data = {
        "id": m_id,
        **m.model_dump()
    }
    return data


@app.get("/memo/{m_id}")
def read_memo(m_id: str):
    if m_id not in MEMOS:
        raise HTTPException(404, detail="Memo not found")
    return MEMOS[m_id]