from .base import ModelAdapter
from transformers import pipeline
from typing import List, Dict, Any

class TranslateKoEnAdapter(ModelAdapter):
    name = "translate-koen"

    def __init__(self, model_id="Helsinki-NLP/opus-mt-ko-en"):
        self.pipe = pipeline(task="translation", model=model_id)
        self.model_used = model_id

    def predict(self, inputs: List[str], params: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
        params = params or {}
        ml = int(params.get("max_length", 256))
        return [{"text": self.pipe(t, max_length=ml)[0]["translation_text"]} for t in inputs]