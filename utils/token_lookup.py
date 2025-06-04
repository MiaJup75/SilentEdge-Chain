import requests
import os

HELIUS_API_KEY = os.getenv("HELIUS_API_KEY")

HELIUS_URL = f"https://api.helius.xyz/v1/token-metadata?api-key={HELIUS_API_KEY}"

def get_token_name(token_address):
    if not HELIUS_API_KEY:
        return None
    try:
        payload = {"mintAccounts": [token_address]}
        response = requests.post(HELIUS_URL, json=payload)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                token_info = data[0]
                return token_info.get("name") or token_info.get("symbol")
    except Exception as e:
        print(f"Token name fetch error: {e}")
    return None
