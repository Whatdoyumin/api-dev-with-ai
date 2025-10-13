from pydantic import BaseModel, Field
from typing import Optional

MAX_ALLOWED = 512

class TranslateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1024, description="입력 텍스트(한글)")
    max_length: Optional[int] = Field(256, ge=16, le=MAX_ALLOWED, description="최대 길이")

class TranslateResponse(BaseModel):
    input_text: str
    translate_text: list
    elapsed_ms: float