# utils/trade.py

def execute_buy(token_symbol, amount_sol, user_id):
    return {
        "status": "success",
        "tx_hash": "placeholder_tx_hash",
        "token": token_symbol,
        "amount": amount_sol,
        "user": user_id
    }

def execute_sale(token_symbol, amount_token, user_id):
    return {
        "status": "success",
        "tx_hash": "placeholder_tx_hash",
        "token": token_symbol,
        "amount": amount_token,
        "user": user_id
    }

def get_wallet_pnl(user_id):
    # Simulated PnL response
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

def get_trade_history(user_id):
    return [
        {"token": "BONK", "action": "buy", "amount": 1000000, "price": 0.00001, "timestamp": "2025-06-03T14:25:00Z"},
        {"token": "SOL", "action": "buy", "amount": 0.5, "price": 150.0, "timestamp": "2025-06-03T14:26:00Z"}
    ]
