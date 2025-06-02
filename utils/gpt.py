# utils/gpt.py

import os
import openai

# Load env variables
openai.api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", 500))
system_prompt = os.getenv("GPT_SYSTEM_PROMPT", "You are a helpful AI assistant for crypto traders.")

def chat_with_gpt(prompt):
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"❌ ChatGPT Error: {str(e)}"
