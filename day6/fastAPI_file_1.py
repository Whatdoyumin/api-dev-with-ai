from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, EmailStr, Field
from uuid import uuid4
from typing import Dict, Optional, List, Union

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

class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=4)

class LoginSuccess(BaseModel):
    status: str = Field(default="ok")
    user_email: EmailStr
    token: str

class LoginError(BaseModel):
    status: str = Field(default="error")
    error_code: str
    message: str

# 성공 또는 실패 모델 둘 다 명시
LoginResponse = Union[LoginSuccess, LoginError]
ACCOUNTS = {"demo@example.com": "pass1234"}

@app.post("/login", response_model=LoginResponse, tags=["auth"])
def login(payload: LoginIn):
    pwd = ACCOUNTS.get(payload.email)
    if not pwd:
        return LoginError(error_code="USER_NOT_FOUND", message="등록되지 않은 이메일입니다.")
    if payload.password != pwd:
        return LoginError(error_code="WRONG_PASSWORD", message="비밀번호가 올바르지 않습니다.")
    
    # 성공 케이스
    fake_token = f"token-{uuid4().hex[:12]}"
    return LoginSuccess(user_email=payload.email, token=fake_token)