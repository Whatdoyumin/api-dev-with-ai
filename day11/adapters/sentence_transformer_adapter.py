from sentence_transformers import SentenceTransformer

class SentenceTransformerAdapter:
    def __init__(self, model_name: str = "intfloat/multilingual-e5-small"):
        self.model_name = model_name
        self._model = SentenceTransformer(model_name)

    def embed(self, texts):
        return self._model.encode(texts, normalize_embeddings=True).tolist()