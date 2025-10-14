import json
import asyncio
from typing import Any, Dict, Tuple, List

# 간단한 캐시 클래스
class _ResultCache:
    def __init__(self):
        self._store: Dict[Tuple[str, str, str], Any] = {}
        
    def get(self, key: Tuple[str, str, str]) -> Any | None:
        return self._store.get(key)
    
    def put(self, key: Tuple[str, str, str], value: Any) -> None:
        self._store[key] = value
        
    # Tuple[str, str, str] -> 요청 (Dcictionary)
    # Any -> 응답
    
def _params_key(params: dict | None) -> str:
    return json.dumps(params or {}, ensure_ascii=False, sort_keys=True)

# 서비스 클래스
class InferService:
    def __init__(self, registry, max_cocurrency: int = 6):
        self.registry = registry
        self.cache = _ResultCache()
        self.schema = asyncio.Semaphore(max_cocurrency) # 동시성 제어
    
    async def _predict_one(self, adapter, text: str, params: dict | None):   # 한 개를 추론하는 함수
        async with self.schema:
            out = await asyncio.to_thread(adapter.predict, inputs=[text], params=params or {})
        return out[0] if isinstance(out, list) and out else out # out이 리스트거나 비어있지 않으면 첫번째 요소 반환, 아니면 out 반환
    
    # 여러 개를 추론하는 함수
    async def infer(self, model: str, texts: List[str], params: dict | None) -> List[Any]:
        try:
            adapter = self.registry.get(model)
        except Exception:
            raise KeyError(model)

        pkey = _params_key(params)
        
        hits: List[Tuple[int, Any]] = []    # 캐시 적중한 것들
        misses: List[Tuple[int, str]] = []   # 캐시 적중하지 않은 것들
        
        for idx, t in enumerate(texts):
            c = self.cache.get((model, t, pkey))
            if c is not None:
                hits.append((idx, c))
            else:
                misses.append((idx, t))
                
        tasks = [self._predict_one(adapter, t, params) for _, t in misses]  # misses에 대해 비동기 작업 생성
        new_results : List[Any] = await asyncio.gather(*tasks) if tasks else [] # tasks가 있으면 gather로 병렬 처리, 없으면 빈 리스트
        
        for (idx, t), r in zip(misses, new_results):
            self.cache.put((model, t, pkey), r)
            
        outputs: List[Any] = [None] * len(texts)
        for i, val in hits:
            outputs[i] = val
        for(i, _), r in zip(misses, new_results):
            outputs[i] = r
            
        return outputs