from openai import OpenAI
import os
from dotenv import load_dotenv
import tiktoken

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# 최대 허용 토큰 수
MAX_USER_MESSAGE_TOKENS = 8000
MODEL_NAME = "gpt-4o-mini"

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
            {"role": "user", "content": user_message}
        ],
        temperature=0.7
    )

    summary = completion.choices[0].message.content
    usage = completion.usage
    return summary, usage
