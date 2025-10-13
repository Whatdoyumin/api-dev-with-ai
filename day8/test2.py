# 감정 분석 실습

from transformers import pipeline

MODEL_ID="Copycats/koelectra-base-v3-generalized-sentiment-analysis"

TEXTS = [
    "완전 만족스러워요. 다시 사고 싶어요!",
    "그냥 무난했어요. 특별히 좋지도 나쁘지도 않네요.",
    "환불하고 싶을 정도로 최악이었어요."
]

sentiment = pipeline(task="text-classification", model=MODEL_ID)

for i, e in enumerate(TEXTS, 1):
    if not e.strip():
        continue
    
    output = sentiment(e)

    print(f'{i}: {output}')

# 결과
# 1: [{'label': '1', 'score': 0.9827128648757935}] -> 긍정일 확률 98.27%
# 2: [{'label': '0', 'score': 0.5604580640792847}] -> 부정일 확률 56.04% (중립에 가까움)
# 3: [{'label': '0', 'score': 0.9988613128662109}] -> 부정일 확률 99.88%