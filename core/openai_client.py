from openai import OpenAI
import tiktoken
from settings import (
    API_KEY, 
    MODEL_NAME, 
    MAX_USER_MESSAGE_TOKENS,
    BASE_URL
)

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=API_KEY)

# URL 관련 함수
def get_base_url():
    return BASE_URL

# 토큰 제한 함수
def truncate_by_tokens(text, max_tokens, model=MODEL_NAME):
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)
    if len(tokens) > max_tokens:
        tokens = tokens[:max_tokens]
    return encoding.decode(tokens)

# GPT 요약 함수
def summarize_with_chatgpt(system_message, user_message):
    user_message = truncate_by_tokens(user_message, MAX_USER_MESSAGE_TOKENS)

    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ],
        temperature=0.7,
    )

    summary = completion.choices[0].message.content
    usage = completion.usage
    return summary, usage
