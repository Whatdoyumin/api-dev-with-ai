from typing import Dict
from .base import ModelAdapter

# 모델을 관리하는 레지스트리
class ModelRegistry:
    def __init__(self):
        self._store: Dict[str, ModelAdapter] = {}
    
    def register(self, adapter: ModelAdapter):
        self._store[adapter.name] = adapter

    def get(self, name: str) -> ModelAdapter:
        if name not in self._store:
            raise KeyError(name)
        return self._store[name]
    
    def list_model(self):
        return list(self._store.keys())
    
registry = ModelRegistry()

from .translate_korean import TranslateKoEnAdapter
from .summarize import SummarizeAdapter
from .sentiment import SentimentAdaptor

adapter1 = TranslateKoEnAdapter()
adapter2 = SummarizeAdapter()
adapter3 = SentimentAdaptor()

registry.register(adapter1)
registry.register(adapter2)
registry.register(adapter3)