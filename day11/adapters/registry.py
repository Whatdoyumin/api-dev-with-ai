from typing import Dict, Any
from .base import ModelAdapter
from .sentence_transformer_adapter import SentenceTransformerAdapter

class ModelRegistry:
    def __init__(self):
        self._store: Dict[str, Any] = {}
        emb = SentenceTransformerAdapter()
        self._store["embedding"] = emb

    def register(self, adapter):
        self._store[adapter.name] = adapter

    def get(self, name: str):
        if name not in self._store:
            raise KeyError(name)
        return self._store[name]

    def list_model(self):
        return list(self._store.keys())
    
registry = ModelRegistry()

from .translate_koen import TranslateKoEnAdapter
from .summarize import SummarizeAdapter
from .sentiment import SentimentAdapter

adapter1 = TranslateKoEnAdapter()
adapter2 = SummarizeAdapter()
adapter3 = SentimentAdapter()

registry.register(adapter1)
registry.register(adapter2)
registry.register(adapter3)