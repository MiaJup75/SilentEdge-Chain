import requests
import os

HELIUS_API_KEY = os.getenv("HELIUS_API_KEY")

def get_token_name(token_address):
    if not HELIUS_API_KEY:
        return None
    try:
        url = f"https://api.helius.xyz/v0/token-metadata?tokenMint={token_address}&api-key={HELIUS_API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get("name") or data.get("symbol")
    except Exception as e:
        print(f"Token name fetch error: {e}")
    return None
