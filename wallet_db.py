import json
import os

WALLET_FILE = "data/wallets.json"
TOKEN_FILE = "data/tokens.json"

def init():
    os.makedirs("data", exist_ok=True)
    for file in [WALLET_FILE, TOKEN_FILE]:
        if not os.path.exists(file):
            with open(file, "w") as f:
                json.dump([], f)

# ===== WALLET FUNCTIONS =====
def get_all_wallets():
    try:
        with open(WALLET_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_wallets(wallets):
    with open(WALLET_FILE, "w") as f:
        json.dump(wallets, f, indent=2)

def add_wallet(address):
    wallets = get_all_wallets()
    if address in [w["address"] for w in wallets]:
        return "❗ Wallet already tracked."
    wallets.append({"address": address, "value": 0})
    save_wallets(wallets)
    return f"✅ Added wallet: {address}"

def remove_wallet(address):
    wallets = get_all_wallets()
    updated = [w for w in wallets if w["address"] != address]
    if len(updated) == len(wallets):
        return "❌ Wallet not found."
    save_wallets(updated)
    return f"🗑️ Removed wallet: {address}"

def load_all():
    get_all_wallets()

# ===== TOKEN FUNCTIONS =====
def get_all_tokens():
    try:
        with open(TOKEN_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_tokens(tokens):
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f, indent=2)

def add_token(symbol, price, market_cap):
    tokens = get_all_tokens()
    tokens.append({"symbol": symbol, "price": price, "market_cap": market_cap})
    save_tokens(tokens)

def clear_tokens():
    save_tokens([])
