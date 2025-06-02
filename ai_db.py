# ai_db.py – stores AI prompts & responses per user

import json
import os

AI_FILE = "data/ai_prompts.json"

def init():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(AI_FILE):
        with open(AI_FILE, "w") as f:
            json.dump({}, f)

def load_data():
    try:
        with open(AI_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(AI_FILE, "w") as f:
        json.dump(data, f, indent=2)

def save_prompt(user_id, prompt, response):
    data = load_data()
    uid = str(user_id)
    if uid not in data:
        data[uid] = []
    data[uid].append({"prompt": prompt, "response": response})
    save_data(data)

def get_prompts(user_id):
    data = load_data()
    return data.get(str(user_id), [])
