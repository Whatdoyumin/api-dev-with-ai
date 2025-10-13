from .base import ModelAdapter
from transformers import pipeline
from typing import List, Dict, Any

class SentimentAdaptor(ModelAdapter):
    name = "sentiment"

    def __init__(self, model_id="Copycats/koelectra-base-v3-generalized-sentiment-analysis"):
        self.pipe = pipeline(task="text-classification", model=model_id)
        self.model_used = model_id

    def predict(self, inputs: List[str], params: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
        out = []
        for t in inputs:
            result = self.pipe(t)[0]
            out.append({"text": result["label"], "score": result["score"]})

        return out