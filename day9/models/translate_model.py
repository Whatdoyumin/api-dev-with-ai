from transformers import pipeline

DEFAULT_ID = "Helsinki-NLP/opus-mt-ko-en"

class TranslateModel:
    def __init__(self, model_id: str = DEFAULT_ID):
        self.pipe = pipeline("translation", model=model_id, tokenizer=model_id)

    def translate(self, text: str, max_length: int = 256):
        result = self.pipe(text, max_length=max_length)
        return result