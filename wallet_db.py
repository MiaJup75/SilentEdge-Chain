import json
import os

DATA_DIR = "data"
WALLET_FILE = os.path.join(DATA_DIR, "wallets.json")
TOKEN_FILE = os.path.join(DATA_DIR, "tokens.json")


def init():
    os.makedirs(DATA_DIR, exist_ok=True)
    for file in [WALLET_FILE, TOKEN_FILE]:
        if not os.path.exists(file):
            with open(file, "w") as f:
                json.dump({}, f)  # initialize as dict for user-specific storage

# ======================= WALLET FUNCTIONS =======================

def get_wallets(user_id):
    wallets = _read_json(WALLET_FILE)
    return wallets.get(str(user_id), [])

def add_wallet(user_id, address):
    wallets = _read_json(WALLET_FILE)
    uid = str(user_id)
    if uid not in wallets:
        wallets[uid] = []
    if address in wallets[uid]:
        return False
    wallets[uid].append(address)
    _write_json(WALLET_FILE, wallets)
    return True

def remove_wallet(user_id, address):
    wallets = _read_json(WALLET_FILE)
    uid = str(user_id)
    if uid not in wallets or address not in wallets[uid]:
        return False
    wallets[uid].remove(address)
    _write_json(WALLET_FILE, wallets)
    return True

def get_all_users():
    wallets = _read_json(WALLET_FILE)
    return list(wallets.keys())

# ======================= TOKEN FUNCTIONS =======================

def get_tokens(user_id):
    tokens = _read_json(TOKEN_FILE)
    return tokens.get(str(user_id), [])

def add_token(user_id, token):
    tokens = _read_json(TOKEN_FILE)
    uid = str(user_id)
    if uid not in tokens:
        tokens[uid] = []
    if token not in tokens[uid]:
        tokens[uid].append(token)
    _write_json(TOKEN_FILE, tokens)


def clear_tokens(user_id):
    tokens = _read_json(TOKEN_FILE)
    uid = str(user_id)
    tokens[uid] = []
    _write_json(TOKEN_FILE, tokens)

# ======================= JSON HELPERS =======================

def _read_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        try:
            return json.load(f)
        except:
            return {}

def _write_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
