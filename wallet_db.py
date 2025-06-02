import json
import os
from datetime import datetime

DATA_FOLDER = "data"
WALLET_FILE = os.path.join(DATA_FOLDER, "wallets.json")

def _ensure_data_file():
    os.makedirs(DATA_FOLDER, exist_ok=True)
    if not os.path.exists(WALLET_FILE):
        with open(WALLET_FILE, "w") as f:
            json.dump([], f)

def get_all_wallets():
    _ensure_data_file()
    try:
        with open(WALLET_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_wallets(wallets):
    with open(WALLET_FILE, "w") as f:
        json.dump(wallets, f, indent=2)

def add_wallet(address, source="manual"):
    wallets = get_all_wallets()
    if any(w.get("address") == address for w in wallets):
        return "❗ Wallet already added."
    new_entry = {
        "address": address,
        "source": source,
        "added_at": datetime.utcnow().isoformat(),
        "pnl": 0,
        "autotrade": False,
        "notes": ""
    }
    wallets.append(new_entry)
    save_wallets(wallets)
    return f"✅ Added wallet: {address}"

def remove_wallet(address):
    wallets = get_all_wallets()
    updated = [w for w in wallets if w.get("address") != address]
    if len(updated) == len(wallets):
        return "❌ Wallet not found."
    save_wallets(updated)
    return f"🗑️ Removed wallet: {address}"

def update_wallet_pnl(address, pnl_change):
    wallets = get_all_wallets()
    for w in wallets:
        if w.get("address") == address:
            w["pnl"] = w.get("pnl", 0) + pnl_change
            break
    save_wallets(wallets)

def toggle_autotrade(address, state: bool):
    wallets = get_all_wallets()
    for w in wallets:
        if w.get("address") == address:
            w["autotrade"] = state
            break
    save_wallets(wallets)

def get_wallet(address):
    wallets = get_all_wallets()
    for w in wallets:
        if w.get("address") == address:
            return w
    return None
