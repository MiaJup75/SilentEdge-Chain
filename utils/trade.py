# utils/trade.py

def execute_buy(token_symbol, amount_sol, user_id):
    # Placeholder logic to simulate a successful buy
    return {
        "status": "success",
        "tx_hash": "placeholder_tx_hash",
        "token": token_symbol,
        "amount": amount_sol,
        "user": user_id
    }

def execute_sell(token_symbol, amount_token, user_id):
    # Placeholder logic to simulate a successful sell
    return {
        "status": "success",
        "tx_hash": "placeholder_tx_hash",
        "token": token_symbol,
        "amount": amount_token,
        "user": user_id
    }

def get_wallet_pnl(user_id):
    # Placeholder PnL logic
    return {
        "user": user_id,
        "tokens": [
            {"symbol": "BONK", "amount": 1200000, "avg_cost": 0.00001, "current_value": 12.0},
            {"symbol": "SOL", "amount": 0.5, "avg_cost": 150.0, "current_value": 160.0}
        ],
        "total_invested": 80.0,
        "total_value": 172.0,
        "profit": 92.0,
        "return_pct": 115.0
    }
