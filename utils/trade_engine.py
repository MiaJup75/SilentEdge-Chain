import os
import requests
from wallet_db import update_wallet_pnl

JUPITER_SWAP_URL = "https://quote-api.jup.ag/v6/swap"

SIMULATED_MODE = os.getenv("TRADING_MODE", "sim") != "real"

def execute_trade(wallet, from_token, to_token, amount):
    if SIMULATED_MODE:
        # Simulated trade (for now)
        print(f"[SIMULATED TRADE] {amount} {from_token} ➝ {to_token} on wallet {wallet}")
        update_wallet_pnl(wallet, 5)  # Dummy gain
        return f"🧪 Simulated trade: {amount} {from_token} ➝ {to_token}"

    # Real trade via Jupiter (placeholder logic)
    payload = {
        "inputMint": from_token,
        "outputMint": to_token,
        "amount": int(amount),
        "slippageBps": 100,
        "userPublicKey": wallet,
        "wrapUnwrapSOL": True
    }

    try:
        response = requests.post(JUPITER_SWAP_URL, json=payload)
        if response.ok:
            update_wallet_pnl(wallet, 5)  # Dummy gain
            return f"✅ Trade executed: {amount} {from_token} ➝ {to_token}"
        else:
            return f"❌ Trade failed: {response.text}"
    except Exception as e:
        return f"🚨 Error during trade: {str(e)}"
