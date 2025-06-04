import requests
from wallet_db import get_tracked_tokens

SOLSCAN_TX_API = "https://public-api.solscan.io/account/splTransfers?account={wallet}&limit=20"
SOLSCAN_HEADERS = {"accept": "application/json"}

def fetch_recent_transfers(wallet_address):
    try:
        response = requests.get(SOLSCAN_TX_API.format(wallet=wallet_address), headers=SOLSCAN_HEADERS)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error fetching txs for {wallet_address}: {e}")
    return []

def check_token_alerts():
    alerts = []
    tokens = get_tracked_tokens()
    for symbol, token in tokens.items():
        token_address = token['address']
        for wallet in token['tracked_wallets']:
            txs = fetch_recent_transfers(wallet)
            for tx in txs:
                if tx.get('tokenAddress') == token_address:
                    short_wallet = wallet[:4] + "..." + wallet[-4:]
                    direction = "Sent" if tx['txFrom'] == wallet else "Received"
                    amount = float(tx['changeAmount']) / (10 ** int(tx.get('decimals', 6)))
                    alert = f"""
<b>🔔 {symbol} Alert!</b>
👤 Wallet: <code>{short_wallet}</code>
💱 Action: {direction}
📊 Amount: {amount:,.2f} {symbol}
🔗 <a href='https://solscan.io/token/{token_address}'>View Token</a>
"""
                    alerts.append(alert)
    return alerts
