from typing import List, Dict, Any

class ModelAdapter:
    name: str
    
    def predict(self, inputs: List[str], params: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
        raise NotImplementedError