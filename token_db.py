import json
import os

TOKEN_DATA_DIR = "data/tokens"

# ===== INIT =====
def init():
    os.makedirs(TOKEN_DATA_DIR, exist_ok=True)

# ===== HELPERS =====
def _get_user_file(user_id):
    return os.path.join(TOKEN_DATA_DIR, f"{user_id}.json")

def _load(user_id):
    path = _get_user_file(user_id)
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)

def _save(user_id, data):
    path = _get_user_file(user_id)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# ===== TOKEN METHODS =====
def get_tokens(user_id):
    return _load(user_id)

def add_token(user_id, token):
    tokens = _load(user_id)
    if token not in tokens:
        tokens.append(token)
        _save(user_id, tokens)

def watch_token(user_id, token):
    add_token(user_id, token)  # Alias for now

def clear_tokens(user_id):
    _save(user_id, [])
