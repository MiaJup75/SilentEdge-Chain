import requests
import os

HELIUS_API_KEY = os.getenv("HELIUS_API_KEY")
HELIUS_URL = f"https://api.helius.xyz/v1/token-metadata?api-key={HELIUS_API_KEY}"

def get_token_name(token_address):
    if not HELIUS_API_KEY:
        print("[Helius] No API key set.")
        return None

    try:
        payload = {"mintAccounts": [token_address]}
        print(f"[Helius] Requesting name for: {token_address}")
        response = requests.post(HELIUS_URL, json=payload)

        print(f"[Helius] Status code: {response.status_code}")
        print(f"[Helius] Response: {response.text}")

        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                token_info = data[0]
                name = token_info.get("name") or token_info.get("symbol")
                print(f"[Helius] Resolved name: {name}")
                return name
    except Exception as e:
        print(f"[Helius] Error during lookup: {e}")

    return None
