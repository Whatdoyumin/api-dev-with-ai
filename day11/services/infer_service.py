from typing import Any, Dict, Tuple, List
import json
import asyncio

class _ResultCache:
    def __init__(self):
        self._store: Dict[Tuple[str, str, str], Any] = {}

    def get(self, key: Tuple[str, str, str]) -> Any | None:
        return self._store.get(key)
    
    def put(self, key: Tuple[str, str, str], value: Any):
        self._store[key] = value

def _params_key(params: dict | None) -> str:
    return json.dumps(params or {}, ensure_ascii=False, sort_keys=True)

class InferService:
    def __init__(self, registry, max_cocurrency: int = 6):
        self.registry = registry
        self.cache = _ResultCache()
        self.sema = asyncio.Semaphore(max_cocurrency)

    async def _predict_one(self, adapter, text: str, params: dict | None):
        async with self.sema:
            out = await asyncio.to_thread(adapter.predict, inputs=[text], params=params or {})
        return out[0] if isinstance(out, list) and out else out
    
    async def infer(self, model: str, texts: List[str], params: dict | None):
        try:
            adapter = self.registry.get(model)
        except Exception:
            raise KeyError(model)
        
        pkey = _params_key(params)

        hits: List[Tuple[int, Any]] = []
        misses: List[Tuple[int, str]] = []

        for idx, t in enumerate(texts):
            c = self.cache.get((model, t, pkey))
            if c is not None:
                hits.append((idx, c))
            else:
                misses.append((idx, t))

        tasks = [self._predict_one(adapter, t, params) for _, t in misses]
        new_results: List[Any] = await asyncio.gather(*tasks) if tasks else []

        for (idx, t), r in zip(misses, new_results):
            self.cache.put((model, t, pkey), r)

        outputs: List[Any] = [None] * len(texts)
        for i, val in hits:
            outputs[i] = val
        for (i, _), r in zip(misses, new_results):
            outputs[i] = r

        return outputs
    
    async def infer_with_detail(self, model: str, texts: List[str], params: dict | None):
        try:
            adapter = self.registry.get(model)
        except:
            raise KeyError(model)
        
        pkey = _params_key(params)

        hits: List[Tuple[int, Any]] = []
        misses: List[Tuple[int, str]] = []

        for idx, t in enumerate(texts):
            c = self.cache.get((model, t, pkey))
            if c is not None:
                hits.append((idx, c))
            else:
                misses.append((idx, t))

        async def _safe(idx: int, text: str):
            async with self.sema:
                try:
                    out = await asyncio.to_thread(adapter.predict, inputs=[text], params=params or {})
                    val = out[0] if isinstance(out, list) and out else out
                    self.cache.put((model, text, pkey), val)
                    return (idx, val, None)
                except Exception as e:
                    return (idx, None, str(e))
                
        results = await asyncio.gather(*[_safe(i, t) for i, t in misses]) if misses else []

        outputs = [None] * len(texts)
        errors = []
        success = 0

        for i, val in hits:
            outputs[i] = val
            success += 1
        for i, val, err in results:
            if err:
                errors.append({
                    "index": i,
                    "text": texts[i],
                    "error": err
                })
            else:
                outputs[i] = val
                success += 1

        return {
            "model": model,
            "count": len(texts),
            "success": success,
            "fail": len(errors),
            "output": outputs,
            "error": errors
        }

        

