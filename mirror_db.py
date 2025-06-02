import os
import json

MIRROR_DIR = "data/mirrors"

def _get_path(user_id):
    return os.path.join(MIRROR_DIR, f"{user_id}.json")

def init():
    os.makedirs(MIRROR_DIR, exist_ok=True)

def add_mirror(user_id, address):
    init()
    data = get_mirrors(user_id)
    if address not in data:
        data.append(address)
        with open(_get_path(user_id), "w") as f:
            json.dump(data, f)

def get_mirrors(user_id):
    try:
        with open(_get_path(user_id), "r") as f:
            return json.load(f)
    except:
        return []

def get_all_users():
    if not os.path.exists(MIRROR_DIR):
        return []
    return [f.split(".")[0] for f in os.listdir(MIRROR_DIR) if f.endswith(".json")]

def toggle_mirror(user_id, address):
    data = get_mirrors(user_id)
    if address in data:
        data.remove(address)
    else:
        data.append(address)
    with open(_get_path(user_id), "w") as f:
        json.dump(data, f)
