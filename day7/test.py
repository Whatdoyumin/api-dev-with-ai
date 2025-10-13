from transformers import pipeline

translator = pipeline("translation", model="Helsinki-NLP/opus-mt-ko-en")


text = '안녕하세요 김민석입니다.'
result = translator(text)[0]['translation_text']

print(result)