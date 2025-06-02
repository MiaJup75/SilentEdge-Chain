# utils/gpt.py

import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

model = os.getenv("OPENAI_MODEL", "gpt-4o")
max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", 500))
system_prompt = os.getenv("GPT_SYSTEM_PROMPT", "You are a helpful AI assistant for crypto traders.")

def chat_with_gpt(prompt):
    chat = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        max_tokens=max_tokens,
        temperature=0.7
    )
    return chat.choices[0].message.content.strip()
