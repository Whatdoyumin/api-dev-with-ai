from .base import ModelAdapter
from transformers import pipeline
from typing import List, Dict, Any

class SummarizeAdapter(ModelAdapter):
    name = "summarize"

    def __init__(self, model_id="gogamza/kobart-summarization"):
        self.pipe = pipeline(task="summarization", model=model_id)
        self.model_used = model_id

    def predict(self, inputs: List[str], params: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
        params = params or {}
        max_len = int(params.get("max_length", 64))
        min_len = int(params.get("min_length", 20))
        return [{"text": self.pipe(t, max_length=max_len, min_length=min_len)[0]["summary_text"]} for t in inputs]