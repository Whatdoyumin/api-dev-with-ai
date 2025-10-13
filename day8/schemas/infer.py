from typing import List, Dict, Any
from pydantic import BaseModel, Field

class InferRequest(BaseModel):
    model: str = Field(..., description="등록된 모델")
    inputs: List[str] = Field(..., min_items=1, max_items=20, description="입력 텍스트 리스트")
    params: Dict[str, Any] | None = Field(default=None, description="모델별 옵션")

class InferResponse(BaseModel):
    model: str
    output: List[Dict]